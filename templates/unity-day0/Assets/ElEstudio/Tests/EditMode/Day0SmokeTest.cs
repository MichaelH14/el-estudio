using System.IO;
using NUnit.Framework;

public class Day0SmokeTest
{
    [Test]
    public void GameMemoryFilesExist()
    {
        string projectRoot = Directory.GetCurrentDirectory();

        Assert.That(File.Exists(Path.Combine(projectRoot, "GDD.md")), Is.True, "Missing GDD.md at project root.");
        Assert.That(File.Exists(Path.Combine(projectRoot, "CHECKPOINT.md")), Is.True, "Missing CHECKPOINT.md at project root.");
        Assert.That(File.Exists(Path.Combine(projectRoot, "CORTE.md")), Is.True, "Missing CORTE.md at project root.");
    }
}
