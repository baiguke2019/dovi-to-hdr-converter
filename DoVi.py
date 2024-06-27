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
        "hdr10": "format=p010le,hwupload_cuda",
        "sdr": "format=yuv420p,hwupload_cuda",
        "hlg": "format=p010le,hwupload_cuda"
    }

    nvenc_params = [
        '-preset', 'slow',
        '-profile:v', 'main10' if encoding_type != 'sdr' else 'main',
        '-b:v', f'{output_bitrate}k',
        '-maxrate:v', f'{output_bitrate}k',
        '-bufsize:v', f'{output_bitrate*2}k'
    ]

    if encoding_type not in video_filters:
        print(f"Invalid encoding type: {encoding_type}")
        return

    ffmpeg_cmd = common_params + [
        '-i', input_file,
        '-vf', video_filters[encoding_type],
        '-c:v', 'hevc_nvenc',
        '-map_chapters', '-1',
        '-an', '-sn'
    ] + nvenc_params + [f'{output_file}_{encoding_type}_slow.mp4']

    subprocess.run(ffmpeg_cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encode video using FFmpeg")
    parser.add_argument("-i", "--input", required=True, help="Input file path")
    parser.add_argument("-o", "--output", required=True, help="Output file path")
    parser.add_argument("--bitrate", type=int, required=True, help="Output bitrate in kbps")
    parser.add_argument("--type", required=True, choices=["hdr10", "sdr", "hlg"], help="Encoding type")

    args = parser.parse_args()
    encode_video(args.input, args.output, args.bitrate, args.type)
