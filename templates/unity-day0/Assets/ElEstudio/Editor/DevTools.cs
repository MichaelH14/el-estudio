using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace ElEstudio.EditorTools
{
    /// <summary>
    /// Herramientas de iteración rápida. El tiempo que tardas desde "cambio algo"
    /// hasta "lo veo en el juego" es la métrica de productividad más importante de
    /// un proyecto: si es alto, arreglarlo rinde más que cualquier feature.
    /// Menú: El Estudio.
    /// </summary>
    public static class DevTools
    {
        const string AlwaysStartFromBootKey = "ElEstudio.AlwaysStartFromBoot";
        const string AlwaysStartFromBootMenu = "El Estudio/Arrancar siempre desde la escena inicial";

        /// <summary>
        /// Con esto activado, dar Play carga primero la escena 0 de Build Settings
        /// (la de arranque) aunque estés editando otra. Evita el clásico "le doy Play
        /// en mi escena de pruebas y todo peta porque no se inicializó nada".
        /// </summary>
        [MenuItem(AlwaysStartFromBootMenu)]
        static void ToggleAlwaysStartFromBoot()
        {
            bool enabled = !EditorPrefs.GetBool(AlwaysStartFromBootKey, false);
            EditorPrefs.SetBool(AlwaysStartFromBootKey, enabled);
            ApplyPlayModeStartScene(enabled);
            Menu.SetChecked(AlwaysStartFromBootMenu, enabled);
            Debug.Log($"[DevTools] Arrancar desde la escena inicial: {(enabled ? "ON" : "OFF")}");
        }

        [MenuItem(AlwaysStartFromBootMenu, true)]
        static bool ToggleAlwaysStartFromBootValidate()
        {
            Menu.SetChecked(AlwaysStartFromBootMenu, EditorPrefs.GetBool(AlwaysStartFromBootKey, false));
            return true;
        }

        [InitializeOnLoadMethod]
        static void RestorePlayModeStartScene()
        {
            ApplyPlayModeStartScene(EditorPrefs.GetBool(AlwaysStartFromBootKey, false));
        }

        static void ApplyPlayModeStartScene(bool enabled)
        {
            if (!enabled)
            {
                EditorSceneManager.playModeStartScene = null;
                return;
            }

            EditorBuildSettingsScene[] scenes = EditorBuildSettings.scenes;
            if (scenes.Length == 0)
            {
                Debug.LogWarning("[DevTools] No hay escenas en Build Settings: no se puede fijar la escena de arranque.");
                return;
            }

            EditorSceneManager.playModeStartScene =
                AssetDatabase.LoadAssetAtPath<SceneAsset>(scenes[0].path);
        }

        /// <summary>Borra el progreso guardado en PlayerPrefs para probar la primera partida.</summary>
        [MenuItem("El Estudio/Borrar progreso guardado (PlayerPrefs)")]
        static void ClearPlayerPrefs()
        {
            if (!EditorUtility.DisplayDialog(
                    "Borrar progreso",
                    "Se borrarán TODOS los PlayerPrefs de este proyecto. No se puede deshacer.",
                    "Borrar", "Cancelar"))
            {
                return;
            }

            PlayerPrefs.DeleteAll();
            PlayerPrefs.Save();
            Debug.Log("[DevTools] PlayerPrefs borrados.");
        }

        /// <summary>Acelera el juego para no esperar animaciones ni timers al iterar.</summary>
        [MenuItem("El Estudio/Velocidad/x0.25 (cámara lenta) &1")]
        static void TimeScaleQuarter() => SetTimeScale(0.25f);

        [MenuItem("El Estudio/Velocidad/x1 (normal) &2")]
        static void TimeScaleNormal() => SetTimeScale(1f);

        [MenuItem("El Estudio/Velocidad/x4 (rápido) &3")]
        static void TimeScaleFast() => SetTimeScale(4f);

        static void SetTimeScale(float scale)
        {
            if (!Application.isPlaying)
            {
                Debug.LogWarning("[DevTools] La velocidad solo se puede cambiar en Play mode.");
                return;
            }

            Time.timeScale = scale;
            Debug.Log($"[DevTools] Time.timeScale = {scale}");
        }

        /// <summary>Abre la memoria viva del proyecto sin salir del editor.</summary>
        [MenuItem("El Estudio/Abrir CHECKPOINT.md")]
        static void OpenCheckpoint()
        {
            string path = System.IO.Path.Combine(
                System.IO.Directory.GetCurrentDirectory(), "CHECKPOINT.md");

            if (!System.IO.File.Exists(path))
            {
                Debug.LogWarning($"[DevTools] No existe {path}");
                return;
            }

            EditorUtility.OpenWithDefaultApp(path);
        }
    }
}
