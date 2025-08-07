from tools.ecosystem.library.foundation.code_executor import CodeExecutorTool


def test_manifest_values():
    tool = CodeExecutorTool()
    assert tool.manifest["interface"]["inputs"][0]["required"] is True
    assert tool.manifest["evolution"]["last_improved"] is None
