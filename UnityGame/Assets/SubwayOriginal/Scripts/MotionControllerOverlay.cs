using UnityEngine;

public class MotionControllerOverlay : MonoBehaviour
{
    private const string ObjectName = "SubwaySurfMotionControllerOverlay";
    private GUIStyle _boxStyle;
    private GUIStyle _titleStyle;
    private GUIStyle _lineStyle;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void Bootstrap()
    {
        if (GameObject.Find(ObjectName) != null)
        {
            return;
        }

        GameObject overlay = new GameObject(ObjectName);
        DontDestroyOnLoad(overlay);
        overlay.AddComponent<MotionControllerOverlay>();
    }

    private void OnGUI()
    {
        EnsureStyles();

        GUILayout.BeginArea(new Rect(12f, 12f, 420f, 116f), _boxStyle);
        GUILayout.Label("Subway Surf + Motion Controller", _titleStyle);
        GUILayout.Label("Creditos: Matheus Siqueira - www.matheussiqueira.dev", _lineStyle);
        GUILayout.Label("Gestos: esquerda, direita, pular, rolar e hoverboard", _lineStyle);
        GUILayout.Label("Teclado: A/Left, D/Right, W/Up/Space, S/Down", _lineStyle);
        GUILayout.EndArea();
    }

    private void EnsureStyles()
    {
        if (_boxStyle != null)
        {
            return;
        }

        _boxStyle = new GUIStyle(GUI.skin.box)
        {
            alignment = TextAnchor.UpperLeft,
            padding = new RectOffset(12, 12, 10, 10),
        };

        _titleStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 16,
            fontStyle = FontStyle.Bold,
            normal = { textColor = Color.white },
        };

        _lineStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 12,
            normal = { textColor = Color.white },
        };
    }
}
