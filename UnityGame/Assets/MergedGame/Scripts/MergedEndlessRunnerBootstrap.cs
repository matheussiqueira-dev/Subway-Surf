using System.Collections.Generic;
using UnityEngine;

public class MergedEndlessRunnerBootstrap : MonoBehaviour
{
    private enum RunnerItemType
    {
        Obstacle,
        LowGate,
        Coin
    }

    private sealed class RunnerItem
    {
        public GameObject Body;
        public RunnerItemType Type;
        public bool Consumed;
    }

    [Header("Player")]
    [SerializeField] private float laneWidth = 2.35f;
    [SerializeField] private float laneMoveSpeed = 12f;
    [SerializeField] private float jumpVelocity = 9.5f;
    [SerializeField] private float gravity = -24f;

    [Header("Runner")]
    [SerializeField] private float startSpeed = 11f;
    [SerializeField] private float maxSpeed = 24f;
    [SerializeField] private float spawnZ = 38f;
    [SerializeField] private float despawnZ = -10f;

    private readonly List<RunnerItem> _items = new List<RunnerItem>();
    private readonly List<Transform> _groundSegments = new List<Transform>();

    private Material _playerMaterial;
    private Material _groundMaterial;
    private Material _laneMaterial;
    private Material _obstacleMaterial;
    private Material _gateMaterial;
    private Material _coinMaterial;
    private Material _shieldMaterial;

    private GameObject _player;
    private Camera _camera;
    private GUIStyle _boxStyle;
    private GUIStyle _titleStyle;
    private GUIStyle _textStyle;
    private GUIStyle _bigStyle;

    private int _lane;
    private int _targetLane;
    private int _lives;
    private int _coins;
    private int _score;
    private float _speed;
    private float _verticalVelocity;
    private float _spawnTimer;
    private float _slideTimer;
    private float _shieldTimer;
    private float _shieldCooldown;
    private float _invincibleTimer;
    private bool _started;
    private bool _gameOver;

    private void Awake()
    {
        CreateMaterials();
        BuildWorld();
        ResetRun();
    }

    private void Update()
    {
        ReadInput();

        if (!_started || _gameOver)
        {
            AnimateIdle();
            return;
        }

        float deltaTime = Time.deltaTime;
        _speed = Mathf.Min(maxSpeed, _speed + deltaTime * 0.18f);
        _score += Mathf.RoundToInt(deltaTime * _speed * 4f);

        UpdateTimers(deltaTime);
        UpdatePlayer(deltaTime);
        UpdateGround(deltaTime);
        UpdateSpawning(deltaTime);
        UpdateItems(deltaTime);
        UpdateCamera(deltaTime);
    }

    private void ReadInput()
    {
        bool left = Input.GetKeyDown(KeyCode.LeftArrow) || Input.GetKeyDown(KeyCode.A);
        bool right = Input.GetKeyDown(KeyCode.RightArrow) || Input.GetKeyDown(KeyCode.D);
        bool jump = Input.GetKeyDown(KeyCode.UpArrow) || Input.GetKeyDown(KeyCode.W);
        bool slide = Input.GetKeyDown(KeyCode.DownArrow) || Input.GetKeyDown(KeyCode.S);
        bool hoverboard = Input.GetKeyDown(KeyCode.Space) || Input.GetKeyDown(KeyCode.H);

        if (!_started && (jump || hoverboard))
        {
            _started = true;
            _gameOver = false;
        }

        if (_gameOver && Input.GetKeyDown(KeyCode.R))
        {
            ResetRun();
            _started = true;
            return;
        }

        if (!_started || _gameOver)
        {
            return;
        }

        if (left)
        {
            MoveLane(-1);
        }

        if (right)
        {
            MoveLane(1);
        }

        if (jump && IsGrounded())
        {
            _verticalVelocity = jumpVelocity;
        }

        if (slide)
        {
            _slideTimer = 0.55f;
        }

        if (hoverboard && _shieldCooldown <= 0f)
        {
            _shieldTimer = 5f;
            _shieldCooldown = 12f;
        }
    }

    private void MoveLane(int direction)
    {
        _targetLane = Mathf.Clamp(_targetLane + direction, -1, 1);
    }

    private void UpdateTimers(float deltaTime)
    {
        _slideTimer = Mathf.Max(0f, _slideTimer - deltaTime);
        _shieldTimer = Mathf.Max(0f, _shieldTimer - deltaTime);
        _shieldCooldown = Mathf.Max(0f, _shieldCooldown - deltaTime);
        _invincibleTimer = Mathf.Max(0f, _invincibleTimer - deltaTime);
    }

    private void UpdatePlayer(float deltaTime)
    {
        Vector3 position = _player.transform.position;
        float targetX = _targetLane * laneWidth;
        position.x = Mathf.Lerp(position.x, targetX, deltaTime * laneMoveSpeed);

        if (!IsGrounded() || _verticalVelocity > 0f)
        {
            _verticalVelocity += gravity * deltaTime;
            position.y += _verticalVelocity * deltaTime;
            if (position.y <= 1f)
            {
                position.y = 1f;
                _verticalVelocity = 0f;
            }
        }

        bool sliding = _slideTimer > 0f && IsGrounded();
        _player.transform.localScale = sliding ? new Vector3(0.82f, 0.55f, 0.82f) : Vector3.one;
        _player.transform.position = position;
        _player.GetComponent<Renderer>().sharedMaterial = _shieldTimer > 0f ? _shieldMaterial : _playerMaterial;

        if (Mathf.Abs(position.x - targetX) < 0.04f)
        {
            _lane = _targetLane;
        }
    }

    private void UpdateGround(float deltaTime)
    {
        for (int i = 0; i < _groundSegments.Count; i++)
        {
            Transform segment = _groundSegments[i];
            segment.position += Vector3.back * _speed * deltaTime;
            if (segment.position.z < -22f)
            {
                segment.position += Vector3.forward * 88f;
            }
        }
    }

    private void UpdateSpawning(float deltaTime)
    {
        _spawnTimer -= deltaTime;
        if (_spawnTimer > 0f)
        {
            return;
        }

        _spawnTimer = Mathf.Lerp(1.15f, 0.62f, Mathf.InverseLerp(startSpeed, maxSpeed, _speed));
        int blockedLane = Random.Range(-1, 2);
        RunnerItemType type = Random.value > 0.72f ? RunnerItemType.LowGate : RunnerItemType.Obstacle;
        SpawnItem(type, blockedLane, spawnZ);

        if (Random.value > 0.35f)
        {
            int coinLane = Random.Range(-1, 2);
            float coinZ = spawnZ + Random.Range(5f, 11f);
            SpawnItem(RunnerItemType.Coin, coinLane, coinZ);
        }
    }

    private void UpdateItems(float deltaTime)
    {
        for (int i = _items.Count - 1; i >= 0; i--)
        {
            RunnerItem item = _items[i];
            item.Body.transform.position += Vector3.back * _speed * deltaTime;

            if (!item.Consumed && IsOverlappingPlayer(item))
            {
                ResolveItem(item);
            }

            if (item.Body.transform.position.z < despawnZ)
            {
                Destroy(item.Body);
                _items.RemoveAt(i);
            }
        }
    }

    private bool IsOverlappingPlayer(RunnerItem item)
    {
        Vector3 playerPosition = _player.transform.position;
        Vector3 itemPosition = item.Body.transform.position;
        bool sameLane = Mathf.Abs(playerPosition.x - itemPosition.x) < laneWidth * 0.45f;
        bool closeZ = Mathf.Abs(playerPosition.z - itemPosition.z) < 1.05f;
        return sameLane && closeZ;
    }

    private void ResolveItem(RunnerItem item)
    {
        if (item.Type == RunnerItemType.Coin)
        {
            item.Consumed = true;
            _coins++;
            _score += 100;
            item.Body.SetActive(false);
            return;
        }

        bool slidingUnderGate = item.Type == RunnerItemType.LowGate && _slideTimer > 0f;
        if (slidingUnderGate || _shieldTimer > 0f || _invincibleTimer > 0f)
        {
            item.Consumed = true;
            item.Body.SetActive(false);
            return;
        }

        _lives--;
        _invincibleTimer = 1.35f;
        item.Consumed = true;
        item.Body.SetActive(false);

        if (_lives <= 0)
        {
            _gameOver = true;
            _started = false;
        }
    }

    private void UpdateCamera(float deltaTime)
    {
        if (_camera == null)
        {
            return;
        }

        Vector3 target = _player.transform.position + new Vector3(0f, 5.5f, -9f);
        _camera.transform.position = Vector3.Lerp(_camera.transform.position, target, deltaTime * 4f);
        _camera.transform.rotation = Quaternion.Lerp(
            _camera.transform.rotation,
            Quaternion.Euler(24f, 0f, 0f),
            deltaTime * 5f
        );
    }

    private void AnimateIdle()
    {
        if (_player == null)
        {
            return;
        }

        Vector3 position = _player.transform.position;
        position.y = 1f + Mathf.Sin(Time.time * 2.4f) * 0.04f;
        _player.transform.position = position;
    }

    private bool IsGrounded()
    {
        return _player.transform.position.y <= 1.001f;
    }

    private void SpawnItem(RunnerItemType type, int lane, float z)
    {
        GameObject body;
        if (type == RunnerItemType.Coin)
        {
            body = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            body.name = "Coin";
            body.transform.localScale = new Vector3(0.48f, 0.48f, 0.12f);
            body.transform.position = new Vector3(lane * laneWidth, 1.25f, z);
            body.GetComponent<Renderer>().sharedMaterial = _coinMaterial;
        }
        else if (type == RunnerItemType.LowGate)
        {
            body = GameObject.CreatePrimitive(PrimitiveType.Cube);
            body.name = "Slide Gate";
            body.transform.localScale = new Vector3(1.95f, 0.35f, 0.7f);
            body.transform.position = new Vector3(lane * laneWidth, 1.55f, z);
            body.GetComponent<Renderer>().sharedMaterial = _gateMaterial;
        }
        else
        {
            body = GameObject.CreatePrimitive(PrimitiveType.Cube);
            body.name = "Obstacle";
            body.transform.localScale = new Vector3(1.25f, 1.2f, 1.05f);
            body.transform.position = new Vector3(lane * laneWidth, 0.7f, z);
            body.GetComponent<Renderer>().sharedMaterial = _obstacleMaterial;
        }

        _items.Add(new RunnerItem { Body = body, Type = type });
    }

    private void ResetRun()
    {
        for (int i = 0; i < _items.Count; i++)
        {
            if (_items[i].Body != null)
            {
                Destroy(_items[i].Body);
            }
        }

        _items.Clear();
        _lane = 0;
        _targetLane = 0;
        _lives = 3;
        _coins = 0;
        _score = 0;
        _speed = startSpeed;
        _verticalVelocity = 0f;
        _spawnTimer = 0.75f;
        _slideTimer = 0f;
        _shieldTimer = 0f;
        _shieldCooldown = 0f;
        _invincibleTimer = 0f;
        _started = false;
        _gameOver = false;

        if (_player != null)
        {
            _player.transform.position = new Vector3(0f, 1f, 0f);
            _player.transform.localScale = Vector3.one;
        }
    }

    private void BuildWorld()
    {
        _player = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        _player.name = "Easy Runner Player";
        _player.transform.position = new Vector3(0f, 1f, 0f);
        _player.GetComponent<Renderer>().sharedMaterial = _playerMaterial;

        for (int i = 0; i < 4; i++)
        {
            GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Cube);
            ground.name = "Moving Track Segment";
            ground.transform.position = new Vector3(0f, -0.08f, i * 22f);
            ground.transform.localScale = new Vector3(laneWidth * 3f + 1.4f, 0.16f, 22f);
            ground.GetComponent<Renderer>().sharedMaterial = _groundMaterial;
            _groundSegments.Add(ground.transform);

            CreateLaneMarker(-laneWidth * 0.5f, i * 22f);
            CreateLaneMarker(laneWidth * 0.5f, i * 22f);
        }

        GameObject leftRail = CreateRail(-laneWidth * 1.5f - 0.6f);
        GameObject rightRail = CreateRail(laneWidth * 1.5f + 0.6f);
        leftRail.name = "Left Safety Rail";
        rightRail.name = "Right Safety Rail";

        GameObject lightObject = new GameObject("Sun");
        Light light = lightObject.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.25f;
        lightObject.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

        GameObject cameraObject = new GameObject("Main Camera");
        _camera = cameraObject.AddComponent<Camera>();
        _camera.tag = "MainCamera";
        _camera.fieldOfView = 64f;
        _camera.backgroundColor = new Color(0.08f, 0.1f, 0.12f);
        _camera.clearFlags = CameraClearFlags.SolidColor;
        _camera.transform.position = new Vector3(0f, 5.5f, -9f);
        _camera.transform.rotation = Quaternion.Euler(24f, 0f, 0f);
    }

    private void CreateLaneMarker(float x, float z)
    {
        GameObject marker = GameObject.CreatePrimitive(PrimitiveType.Cube);
        marker.name = "Lane Marker";
        marker.transform.position = new Vector3(x, 0.03f, z);
        marker.transform.localScale = new Vector3(0.06f, 0.04f, 16f);
        marker.GetComponent<Renderer>().sharedMaterial = _laneMaterial;
        _groundSegments.Add(marker.transform);
    }

    private GameObject CreateRail(float x)
    {
        GameObject rail = GameObject.CreatePrimitive(PrimitiveType.Cube);
        rail.transform.position = new Vector3(x, 0.45f, 15f);
        rail.transform.localScale = new Vector3(0.16f, 0.9f, 90f);
        rail.GetComponent<Renderer>().sharedMaterial = _laneMaterial;
        return rail;
    }

    private void CreateMaterials()
    {
        _playerMaterial = CreateMaterial(new Color(0.08f, 0.62f, 1f));
        _shieldMaterial = CreateMaterial(new Color(0.2f, 1f, 0.75f));
        _groundMaterial = CreateMaterial(new Color(0.18f, 0.2f, 0.21f));
        _laneMaterial = CreateMaterial(new Color(0.95f, 0.95f, 0.82f));
        _obstacleMaterial = CreateMaterial(new Color(0.95f, 0.24f, 0.22f));
        _gateMaterial = CreateMaterial(new Color(1f, 0.6f, 0.14f));
        _coinMaterial = CreateMaterial(new Color(1f, 0.86f, 0.18f));
    }

    private static Material CreateMaterial(Color color)
    {
        Shader shader = Shader.Find("Standard");
        if (shader == null)
        {
            shader = Shader.Find("Universal Render Pipeline/Lit");
        }
        if (shader == null)
        {
            shader = Shader.Find("Sprites/Default");
        }
        Material material = new Material(shader);
        material.color = color;
        return material;
    }

    private void OnGUI()
    {
        EnsureGuiStyles();

        GUILayout.BeginArea(new Rect(12f, 12f, 420f, 156f), _boxStyle);
        GUILayout.Label("Subway Surf Vision Runner", _titleStyle);
        GUILayout.Label("Creditos: Matheus Siqueira - www.matheussiqueira.dev", _textStyle);
        GUILayout.Label("A/Left e D/Right mudam de faixa. W/Up pula. S/Down rola.", _textStyle);
        GUILayout.Label("Space/H ativa hoverboard. Gestos do controlador enviam essas teclas.", _textStyle);
        GUILayout.Label("Score " + _score + "   Coins " + _coins + "   Lives " + _lives + "   Speed " + _speed.ToString("0.0"), _textStyle);
        GUILayout.EndArea();

        if (!_started)
        {
            string message = _gameOver ? "Game over - pressione R para recomecar" : "Pressione W, Up ou Space para iniciar";
            GUI.Label(new Rect(0f, Screen.height * 0.42f, Screen.width, 80f), message, _bigStyle);
        }

        if (_shieldTimer > 0f)
        {
            GUI.Label(new Rect(0f, Screen.height - 70f, Screen.width, 40f), "Hoverboard ativo: " + _shieldTimer.ToString("0.0") + "s", _bigStyle);
        }
    }

    private void EnsureGuiStyles()
    {
        if (_boxStyle != null)
        {
            return;
        }

        _boxStyle = new GUIStyle(GUI.skin.box)
        {
            alignment = TextAnchor.UpperLeft,
            padding = new RectOffset(12, 12, 10, 10)
        };

        _titleStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 18,
            fontStyle = FontStyle.Bold,
            normal = { textColor = Color.white }
        };

        _textStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 13,
            normal = { textColor = Color.white }
        };

        _bigStyle = new GUIStyle(GUI.skin.label)
        {
            alignment = TextAnchor.MiddleCenter,
            fontSize = 28,
            fontStyle = FontStyle.Bold,
            normal = { textColor = Color.white }
        };
    }
}
