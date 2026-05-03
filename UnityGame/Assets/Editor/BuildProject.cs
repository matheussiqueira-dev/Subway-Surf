using System.IO;
using UnityEditor;

public static class BuildProject
{
    private const string ScenePath = "Assets/Scenes/Main.unity";
    private const string OutputPath = "Builds/Windows/SubwaySurfVisionRunner.exe";

    public static void BuildWindows()
    {
        Directory.CreateDirectory(Path.GetDirectoryName(OutputPath));

        BuildPlayerOptions options = new BuildPlayerOptions
        {
            scenes = new[] { ScenePath },
            locationPathName = OutputPath,
            target = BuildTarget.StandaloneWindows64,
            options = BuildOptions.None
        };

        BuildPipeline.BuildPlayer(options);
    }
}
