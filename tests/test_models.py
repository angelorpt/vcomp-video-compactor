from pathlib import Path

from vcomp.models import CompressionReport, CompressionResult, OutputMode, VideoFile


def test_video_file_properties():
    vf = VideoFile(path=Path("/path/to/video.mp4"), size_bytes=1000)
    assert vf.extension == ".mp4"
    assert vf.stem == "video"


def test_compression_result_properties():
    r = CompressionResult(
        input_path=Path("in.mp4"),
        output_path=Path("out.mp4"),
        success=True,
        input_size=1000,
        output_size=300,
    )
    assert r.saved_bytes == 700
    assert r.ratio == 30.0


def test_compression_result_zero_input():
    r = CompressionResult(
        input_path=Path("in.mp4"),
        output_path=Path("out.mp4"),
        success=True,
        input_size=0,
        output_size=0,
    )
    assert r.ratio == 0.0


def test_compression_report_properties():
    report = CompressionReport()
    r1 = CompressionResult(Path("a.mp4"), Path("a_c.mp4"), success=True, input_size=100, output_size=40)
    r2 = CompressionResult(Path("b.mp4"), Path("b_c.mp4"), success=True, input_size=200, output_size=80)
    report.results = [r1, r2]
    assert report.total_input_size == 300
    assert report.total_output_size == 120
    assert report.total_saved == 180
    assert len(report.successful) == 2


def test_compression_report_with_errors():
    report = CompressionReport()
    ok = CompressionResult(Path("a.mp4"), Path("a_c.mp4"), success=True, input_size=100, output_size=50)
    err = CompressionResult(Path("b.mp4"), Path("b_c.mp4"), success=False, input_size=200, output_size=0)
    report.results = [ok, err]
    assert report.total_input_size == 100
    assert ok in report.successful
    assert err not in report.successful


def test_compression_report_empty():
    report = CompressionReport()
    assert report.total_input_size == 0
    assert report.total_output_size == 0
    assert report.total_saved == 0
    assert report.successful == []


def test_output_mode_values():
    assert OutputMode.KEEP.value == "keep"
    assert OutputMode.REPLACE.value == "replace"
    assert OutputMode.CLONE.value == "clone"
    assert len(OutputMode) == 3
