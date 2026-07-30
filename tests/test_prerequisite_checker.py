from vcomp.prerequisite_checker import check_ffmpeg


def test_check_ffmpeg_found():
    assert check_ffmpeg() is True
