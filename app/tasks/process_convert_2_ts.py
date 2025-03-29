import os
import subprocess
import dramatiq

@dramatiq.actor
def segment_video(file_path: str, mode: str = "time", value: int = None, fps: int = None):
    """
    根据输入视频分辨率转换输出格式：
      - 若源视频长边 ≥ 1080，则转换为 1080p 和 720p 两种格式；
      - 否则只转换为 720p。

    同时支持两种切片模式：
      - mode=="time": 按时间切片，默认时长根据文件大小动态设置；
      - mode=="size": 按大小切片，默认 8MB。

    可选参数 fps 用于压缩模式下指定输出帧率（默认 25fps）。

    输出 TS 分片文件存放在当前工作目录下的 /static/convert/vol/<格式>/，
    输出文件名模板为 {原文件名}_segment_%03d.ts。
    同时生成对应的 .m3u8 文件。
    """
    try:
        # 1. 获取源视频分辨率
        ffprobe_cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=p=0", file_path
        ]
        result = subprocess.run(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        dims_str = result.stdout.strip()
        try:
            dims = dims_str.split(',')
            if len(dims) >= 2:
                width = int(dims[0])
                height = int(dims[1])
            else:
                width = 0
                height = int(dims[0])
            print(f"获取视频分辨率：宽 {width} 像素, 高 {height} 像素")
        except Exception as e:
            print(f"获取视频分辨率失败，默认设为 1280x720：{e}")
            width = 1280
            height = 720

        # 2. 根据长边判断输出格式
        long_side = max(width, height)
        # 2. 根据高度判断输出格式
        formats = []
        if height >= 1080:
            formats.append(("1080p", "scale=-2:1080"))
            formats.append(("720p", "scale=-2:720"))
        else:
            formats.append(("720p", "scale=-2:720"))

        # 3. 设置切片默认参数
        file_size = os.path.getsize(file_path)
        if value is None:
            if mode == "time":
                if file_size < 100 * 1024 * 1024:
                    value = 8  # 小于100MB：5秒
                elif file_size < 300 * 1024 * 1024:
                    value = 12  # 100MB-300MB：8秒
                else:
                    value = 18  # 大于等于300MB：15秒
            elif mode == "size":
                value = 8 * 1024 * 1024  # 默认8MB
            else:
                raise ValueError("mode 必须为 'time' 或 'size'")

        if fps is None:
            fps = 25  # 默认帧率

        # 输出根目录：保持原有结构
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base_output_dir = os.path.join(BASE_DIR, "static", "convert", "vods")
        print(f"工作目录:{base_output_dir}")
        os.makedirs(base_output_dir, exist_ok=True)

        # 提取源文件基本名
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        # 4. 针对每种格式进行转码、切片并生成 .m3u8
        for label, scale_filter in formats:
            out_dir = os.path.join(base_output_dir, label)
            os.makedirs(out_dir, exist_ok=True)
            # output_pattern = os.path.join(out_dir, f"{base_name}_segment_%03d.ts")
            output_pattern = os.path.join(out_dir, f"{base_name}_segment_%03d.ts")

            m3u8_file = os.path.join(out_dir, f"{base_name}.m3u8")

            # 构造 ffmpeg 命令（直接生成 HLS）
            command = [
                "ffmpeg", "-i", file_path,
                "-r", str(fps),
                "-vf", scale_filter,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
                "-g", str(int(value * fps)),  # GOP 长度
                "-keyint_min", str(int(value * fps)),
                "-sc_threshold", "0",
                "-c:a", "aac", "-b:a", "96k", "-ar", "44100", "-ac", "2",
                "-flush_packets", "1",
                "-movflags", "+faststart",
                "-force_key_frames", f"expr:gte(t,n_forced*{value})",
                "-f", "hls",
                "-hls_time", str(value),
                "-hls_segment_type", "mpegts",
                "-hls_playlist_type", "vod",
                "-hls_segment_filename", output_pattern,
                m3u8_file
            ]

            print(f"【{label}】执行命令: {' '.join(command)}")
            subprocess.run(command, check=True)
            print(f"【{label}】视频转码及切片完成：{file_path}，切片模式：{mode}，值：{value}，FPS: {fps}")

    except Exception as e:
        print(f"处理视频 {file_path} 时出错：{e}")


if __name__ == "__main__":
    # 测试用例
    segment_video("input.mp4", mode="time")