import argparse
import subprocess

def encode_video(input_file, output_file, output_bitrate, encoding_type):
    common_params = [
        'ffmpeg',
        '-nostdin',
        '-loglevel', 'error',
        '-stats',
        '-y',
        '-hwaccel', 'cuda',
        '-hwaccel_output_format', 'cuda'
    ]

    video_filters = {
        "hdr10": "hwupload_cuda,scale_npp=format=yuv420p10le,hwdownload,format=yuv420p10le",
        "sdr": "hwupload_cuda,scale_npp=format=yuv420p,hwdownload,format=yuv420p",
        "hlg": "hwupload_cuda,scale_npp=format=yuv420p10le,hwdownload,format=yuv420p10le"
    }

    nvenc_params = {
        "hdr10": "preset=slow:profile=main10:cbr=1:bitrate={}:maxrate={}:bufsize={}".format(output_bitrate, output_bitrate, output_bitrate*2),
        "sdr": "preset=slow:profile=main:cbr=1:bitrate={}:maxrate={}:bufsize={}".format(output_bitrate, output_bitrate, output_bitrate*2),
        "hlg": "preset=slow:profile=main10:cbr=1:bitrate={}:maxrate={}:bufsize={}".format(output_bitrate, output_bitrate, output_bitrate*2)
    }

    if encoding_type not in video_filters or encoding_type not in nvenc_params:
        print(f"Invalid encoding type: {encoding_type}")
        return

    ffmpeg_cmd = common_params + [
        '-i', input_file,
        '-vf', video_filters[encoding_type],
        '-c:v', 'hevc_nvenc',
        '-map_chapters', '-1',
        '-an', '-sn',
        '-b:v', f'{output_bitrate}k',
        '-preset', 'slow',
        '-profile:v', 'main10' if encoding_type != 'sdr' else 'main',
        f'{output_file}_{encoding_type}_slow.mp4'
    ]

    subprocess.run(ffmpeg_cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encode video using FFmpeg")
    parser.add_argument("-i", "--input", required=True, help="Input file path")
    parser.add_argument("-o", "--output", required=True, help="Output file path")
    parser.add_argument("--bitrate", type=int, required=True, help="Output bitrate in kbps")
    parser.add_argument("--type", required=True, choices=["hdr10", "sdr", "hlg"], help="Encoding type")

    args = parser.parse_args()
    encode_video(args.input, args.output, args.bitrate, args.type)
