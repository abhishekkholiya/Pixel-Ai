from stability_sdk.animation import AnimationArgs, Animator
from stability_sdk import api
from stability_sdk.utils import create_video_from_frames
from tqdm import tqdm

STABILITY_HOST = "grpc.stability.ai:443"
STABILITY_KEY = "sk-dSqynjKMho8UFL5f6P53F9gBgzEaDY2qek4XZMusHovjEpNh"

context = api.Context(STABILITY_HOST,STABILITY_KEY)

args = AnimationArgs()
args.interpolate_prompts= True
args.locked_seed = True
args.max_frames = 48
args.seed = 42
args.strength_curve = "0:(0)"
args.diffusion_cadence_curve = "0:(4)"
args.cadence_interp = "film"

animation_prompts={
    0:"a photo of a baby boy",
    24:"a photo of an adult human"
}
negative_prompt = ""

animator = Animator(
    api_context=context,
    animation_prompts=animation_prompts,
    negative_prompt=negative_prompt,
    args=args,
    out_dir="video_01"
)


for _ in tqdm(animator.render(), total=args.max_frames):
    pass
create_video_from_frames(animator.out_dir, "video.mp4", fps=24)
