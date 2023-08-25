import discord 
from discord import app_commands
from discord.ext import commands
import threading


from fileinput import filename
from PIL import Image
import io
from stability_sdk import client,api
from stability_sdk.animation import AnimationArgs, Animator
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from stability_sdk.utils import create_video_from_frames
from tqdm import tqdm


#intents required
intents = discord.Intents.default()
intents.message_content = True
intents.members = True


#stability-api part
api_key ='sk-dSqynjKMho8UFL5f6P53F9gBgzEaDY2qek4XZMusHovjEpNh'
stability_api = client.StabilityInference(
    key=api_key,
    verbose=True
)

def animate(arg1,arg2):
    STABILITY_HOST = "grpc.stability.ai:443"
    STABILITY_KEY = "sk-dSqynjKMho8UFL5f6P53F9gBgzEaDY2qek4XZMusHovjEpNh"

    context = api.Context(STABILITY_HOST,STABILITY_KEY)
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

@bot.event
async def on_ready():
    print('Bot is ready')
    await bot.tree.sync()
    print("commands synced")



@bot.tree.command(name="hello",description="Bot responds with greeting")
async def hello(interaction:discord.Interaction):
    print("reached here")
    await interaction.response.send_message(f"Hey {interaction.user.mention}, do you like the slash command?")

@bot.tree.command(name="wave",description="Bot responds with wave")
@app_commands.describe(wave_at = "whom to wave?")
async def wave(interaction:discord.Interaction,wave_at:str):
    print(wave_at)
    await interaction.response.send_message(f"{interaction.user.name} waved at {wave_at} ")

@bot.command()
async def make(ctx, *, prompt):
    message = await ctx.send(f"Generating ✨ results for ({prompt})")
    result = stability_api.generate(prompt=prompt)
    for resp in result:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                message = await ctx.send("The prompt you gave is against our policies")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                arr = io.BytesIO(artifact.binary)
                img.save(arr,format="PNG")
                arr.seek(0)
                file = discord.File(arr,filename="result.png")
                await message.edit(content=f"Showing Results ✨ for {prompt}")
                await ctx.send(file=file)

@bot.tree.command(name="image",description="Bot makes image of your wish")
@app_commands.describe(make="what to make?")
async def image(interaction:discord.Interaction,make:str):
    print(discord.Interaction)
    message = await interaction.response.send_message(f"Generating ✨ results for ({make})")
    result = stability_api.generate(prompt=make)
    print(result)
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
                await interaction.delete_original_response()
                embed = discord.Embed(title =f"Generated ✨ Results for ({make})")
                embed.set_image(url="attachment://result.png")
                embed.set_author(name=interaction.user.name)
                await interaction.channel.send(embed=embed,file=file)


@bot.tree.command(name="video",description="Bot makes video of your wish")
@app_commands.describe(character="choose first character",character2="choose second character")
async def video(interaction:discord.Interaction,character:str,character2:str):  
    try: 
        await interaction.response.send_message(content=f"Generating Video ✨ for ({character}) and ({character2})")
        thread = threading.Thread(target=animate,args=(character,character2))
        thread.start()
    except:
        await interaction.response.send_message(content="You have just tried the command!")
   
bot.run('ODY0MDUzNDQ2MDM3OTk1NTUw.YOv2eg.voA9GlXhxYgXubktKHdDUID5Ztw')