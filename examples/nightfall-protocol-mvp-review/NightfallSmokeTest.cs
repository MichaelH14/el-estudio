using System.Linq;
using NUnit.Framework;
using UnityEngine;

public class NightfallSmokeTest
{
    [Test]
    public void SceneContainsCoreLoopActors()
    {
        string[] requiredNames =
        {
            "Player",
            "Stalker",
            "ExitGate"
        };

        string[] sceneNames = Object.FindObjectsByType<GameObject>(FindObjectsSortMode.None)
            .Select(gameObject => gameObject.name)
            .ToArray();

        foreach (string requiredName in requiredNames)
        {
            Assert.That(sceneNames.Any(sceneName => sceneName.Contains(requiredName)), Is.True, $"Missing {requiredName}.");
        }
    }
}
