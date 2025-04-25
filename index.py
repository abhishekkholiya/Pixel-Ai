import discord 
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
import threading
import os


from fileinput import filename
from PIL import Image
import io
from stability_sdk import client,api
from stability_sdk.animation import AnimationArgs, Animator
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from stability_sdk.utils import create_video_from_frames
from tqdm import tqdm


load_dotenv()
#intents required
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot_token = os.getenv("BOT_TOKEN")

#stability-api part
api_key = os.getenv('STABILITY_API_KEY')

stability_api = client.StabilityInference(
    key=api_key,
    verbose=True
)

def animate(arg1,arg2):
    STABILITY_HOST = os.getenv('API_HOST')

    context = api.Context(STABILITY_HOST,api_key)
    print(arg1,arg2)
    args = AnimationArgs()
    args.interpolate_prompts= True
    args.locked_seed = True
    args.max_frames = 48
    args.seed = 42
    args.strength_curve = "0:(0)"
    args.diffusion_cadence_curve = "0:(4)"
    args.cadence_interp = "film"

    animation_prompts={
        0:f"{arg1}",
        24:f"{arg2}"
    }
    print(animation_prompts)
    negative_prompt = ""

    animator = Animator(
        api_context=context,
        animation_prompts=animation_prompts,
        negative_prompt=negative_prompt,
        args=args,
        out_dir=f"video_{arg1}"
    )


    for _ in tqdm(animator.render(), total=args.max_frames):
        pass
    create_video_from_frames(animator.out_dir, f"{arg1}.mp4", fps=24)


   
bot = commands.Bot(command_prefix=">",intents= intents)



#here starts the discord bot part





@bot.tree.command(name="hello",description="Bot responds with greeting")
async def hello(interaction:discord.Interaction):
    print("reached here")
    await interaction.response.send_message(f"Hey {interaction.user.mention}, do you like the slash command?")
    
@bot.tree.command(name="creator",description="Bot responds with creator name")
async def creator(interaction:discord.Interaction):
    print("reached here")
    await interaction.response.send_message(f"Hey {interaction.user.mention}, I am created by mrkholiya#5152 and I am still learning about this beautiful world!")


@bot.tree.command(name="wave",description="Bot responds with wave")
@app_commands.describe(wave_at = "whom to wave?")
async def wave(interaction:discord.Interaction,wave_at:str):
    print(wave_at)
    await interaction.response.send_message(f"{interaction.user.name} waved at {wave_at} ")

#new command starts here
@bot.tree.command(name="imagine",description="Bot makes image of your wish")
@app_commands.describe(make="prompt")
async def imagine(interaction:discord.Interaction,make:str):
    message = await interaction.response.send_message(f"Generating ✨ results for ({make})")
    result = stability_api.generate(prompt=make)
    for resp in result:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                await interaction.delete_original_response()
                message = await interaction.channel.send    ("The prompt you gave is against our policies")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                arr = io.BytesIO(artifact.binary)
                img.save(arr,format="PNG")
                arr.seek(0)
                file = discord.File(arr,filename="result.png")
               
                embed = discord.Embed(title =f"Generated ✨ Results for ({make})")
                embed.set_image(url="attachment://result.png")
                embed.set_author(name=interaction.user.name)
                msg = await interaction.original_response()
               # await msg.edit(embed=embed)
                await interaction.channel.send(file=file)

@bot.tree.command(name="multiple",description="Bot generates multiple images for same prompt")
@app_commands.describe(make="prompt")
async def multiple(interaction:discord.Interaction,make:str):
    message = await interaction.response.send_message(f"Generating ✨ multiple results for ({make})")
    result = stability_api.generate(prompt=make)
    for resp in result:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                await interaction.delete_original_response()
                message = await interaction.channel.send    ("The prompt you gave is against our policies")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                arr = io.BytesIO(artifact.binary)
                img.save(arr,format="PNG")
                arr.seek(0)
                
                answers = stability_api.generate(
                    prompt=f"{make}",
                    #init_image=img, 
                    #start_schedule=0.01, # Set the strength of our prompt in relation to our initial image.
                    steps=50, 
                    cfg_scale=8.0, 
                    width=1024, 
                    height=1024, 
                    samples=3, 
                    sampler=generation.SAMPLER_K_DPMPP_2M 
                )
                for resp in answers:
                    for artifact in resp.artifacts:
                        if artifact.finish_reason == generation.FILTER:
                            warnings.warn(
                                "Your request activated the API's safety filters and could not be processed."
                                "Please modify the prompt and try again.")
                        if artifact.type == generation.ARTIFACT_IMAGE:
                            global img2
                            img2 = Image.open(io.BytesIO(artifact.binary)) # Set our resulting initial image generations as 'img2' to avoid overwriting our previous 'img' generation.
                            img2.save(str(artifact.seed)+ ".png") # Save our generated images with their seed number as the filename.
                            
                            img2 = Image.open(io.BytesIO(artifact.binary))
                            arr = io.BytesIO(artifact.binary)
                            img2.save(arr,format="PNG")
                            arr.seek(0)
                            file = discord.File(arr,filename="result.png")
                            
                            
                       
                            
                            embed = discord.Embed(title =f"Generated ✨ Results for ({make})")
                            embed.set_image(url="attachment://result.png")
                            embed.set_author(name=interaction.user.name)
                            msg = await interaction.original_response()
                        # await msg.edit(embed=embed)
                            await interaction.channel.send(file=file)

                            

   
#@bot.tree.command(name="video",description="Bot makes video of your wish")
#@app_commands.describe(character="choose first character",character2="choose second character")
#async def video(interaction:discord.Interaction,character:str,character2:str):  
 #   try: 
 #       await interaction.response.send_message(content=f"Generating Video ✨ for ({character}) and ({character2})")
  #      thread = threading.Thread(target=animate,args=(character,character2))
   #     thread.start()
   # except:
    #    await interaction.response.send_message(content="You have just tried the command!")


@bot.event
async def on_ready():
    print('Bot is ready')
    await bot.tree.sync()
    print("commands synced")
    
   
# bot.run("ODg2MjYzMDAwNTQ0MTg2NDg5.G5ESzv.AvgGeWEKhRBD5g7v9mV2WJ77CdNfPAIrY7CrG4")
bot.run(bot_token)