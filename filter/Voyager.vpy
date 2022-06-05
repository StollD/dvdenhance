##
## VapourSynth filter for Star Trek Voyager (PAL DVD)
##

import havsfunc
import muvsfunc
from vapoursynth import GRAY, core

VIDEO = "$(video)$"

# Set the amount of threads used
core.num_threads = 12

# Load the video
clip = core.lsmas.LWLibavSource(VIDEO)

# Field match the clip to restore progressive frames
clip = core.vivtc.VFM(clip, order=1)

# Remove combing artifacts
clip = havsfunc.santiag(clip)

# Remove MPEG2 compression artifacts
clip = havsfunc.Deblock_QED(clip, uv=1)

# Remove rainbowing
clip = core.bifrost.Bifrost(clip, interlaced=False)

# Remove luma noise
clip = havsfunc.SMDegrain(
    clip,
    plane=0,
    chroma=True,
    RefineMotion=True,
    truemotion=False,
    contrasharp=True,
)

# Remove chroma noise
clip = core.knlm.KNLMeansCL(clip, d=2, h=4, channels="UV")

# Extract the luma
luma = core.std.ShufflePlanes(clip, 0, GRAY)

# Seperate small detail from the rest of the image
base = core.fft3dfilter.FFT3DFilter(luma, sigma=10)
detail = core.std.MakeDiff(luma, base)

# Remove banding
base = muvsfunc.GradFun3(base)

# Remove softness from the PAL upscale
base = core.descale.Debilinear(base, 640, 480)
base = havsfunc.santiag(base, fw=720, fh=576)

# Remove ringing and halos
base = havsfunc.HQDeringmod(base)
base = havsfunc.FineDehalo(base)

# Recombine base and detail
luma = core.std.MergeDiff(base, detail)

# Recombine luma and chroma
clip = muvsfunc.MergeChroma(luma, clip)

# Readd more noise
clip = core.grain.Add(clip)

clip.set_output()
