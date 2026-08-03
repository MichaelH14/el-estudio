#if UNITY_EDITOR
using System;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Object = UnityEngine.Object;

namespace NightfallProtocol.Editor
{
    public static class NightfallSmokeTest
    {
        private const string ScenePath = "Assets/NightfallProtocol/Scenes/MvpScene.unity";

        public static void Run()
        {
            try
            {
                EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
                RuntimeBootstrap bootstrap = Object.FindObjectOfType<RuntimeBootstrap>();
                Require(bootstrap != null, "RuntimeBootstrap missing from MVP scene.");

                bootstrap.BuildScene();

                GameManager gameManager = Object.FindObjectOfType<GameManager>();
                Require(gameManager != null, "GameManager was not created.");
                Require(gameManager.gridMap != null, "GridMap was not assigned.");
                Require(gameManager.playerRunner != null, "Player runner was not assigned.");
                Require(gameManager.stalker != null, "Stalker was not assigned.");
                Require(gameManager.exitZone != null, "Exit zone was not assigned.");
                Require(gameManager.runners.Count == 3, $"Expected 3 runners, got {gameManager.runners.Count}.");
                Require(gameManager.objectives.Count == 3, $"Expected 3 objectives, got {gameManager.objectives.Count}.");

                ValidateSpawnCells(gameManager);
                ValidateCriticalPaths(gameManager);

                Debug.Log("Nightfall smoke test passed: scene builds, agents spawn, objectives exist, and paths resolve.");
                EditorApplication.Exit(0);
            }
            catch (Exception exception)
            {
                Debug.LogException(exception);
                EditorApplication.Exit(1);
            }
        }

        private static void ValidateSpawnCells(GameManager gameManager)
        {
            GridMap gridMap = gameManager.gridMap;
            foreach (RunnerAgent runner in gameManager.runners)
            {
                Require(runner != null, "Runner list contains null.");
                Require(gridMap.IsWalkable(gridMap.WorldToCell(runner.transform.position)), $"{runner.name} spawned in a wall.");
            }

            Require(gridMap.IsWalkable(gridMap.WorldToCell(gameManager.stalker.transform.position)), "Stalker spawned in a wall.");
            Require(gridMap.IsWalkable(gridMap.WorldToCell(gameManager.exitZone.transform.position)), "Exit spawned in a wall.");
        }

        private static void ValidateCriticalPaths(GameManager gameManager)
        {
            GridMap gridMap = gameManager.gridMap;
            ObjectiveStation nearestObjective = gameManager.FindNearestIncompleteObjective(gameManager.playerRunner.transform.position);
            Require(nearestObjective != null, "No incomplete objective found.");

            Require(
                gridMap.FindWorldPath(gameManager.playerRunner.transform.position, nearestObjective.transform.position).Count > 0,
                "No path from player to nearest objective."
            );

            Require(
                gridMap.FindWorldPath(gameManager.stalker.transform.position, gameManager.playerRunner.transform.position).Count > 0,
                "No path from stalker to player."
            );

            Require(
                gridMap.FindWorldPath(nearestObjective.transform.position, gameManager.exitZone.transform.position).Count > 0,
                "No path from objective area to exit."
            );
        }

        private static void Require(bool condition, string message)
        {
            if (!condition)
            {
                throw new InvalidOperationException(message);
            }
        }
    }
}
#endif
