<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$host = 'localhost';
$dbname = getenv('DB_NAME') ?: '3taldea';
$user = getenv('DB_USER') ?: 'root';
$password = getenv('DB_PASSWORD') ?: '1WMG2023';
$port = getenv('DB_PORT') ?: 3306;

try {
    $pdo = new PDO("mysql:host=$host;port=$port;dbname=$dbname;charset=utf8", $user, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Error de conexión: ' . $e->getMessage()]);
    exit;
}

// Lógica de endpoints
$endpoint = $_GET['endpoint'] ?? '';

switch ($endpoint) {
    case 'pedidos_por_servidor':
        $stmt = $pdo->query("
            SELECT l.izena AS Zerbitzaria, COUNT(ep.id) AS Eskaera_guztiak
            FROM eskaera_platera ep
            JOIN eskaera e ON ep.eskaera_id = e.id
            JOIN mahaia m ON e.mesa_id = m.id
            JOIN langilea l ON m.id = l.id
            GROUP BY l.izena
        ");
        $data = $stmt->fetchAll(PDO::FETCH_ASSOC);
        echo json_encode($data);
        break;

    case 'pedidos_por_plato':
        $stmt = $pdo->query("
            SELECT p.izena AS Platera, COUNT(ep.id) AS Eskaera_guztiak
            FROM eskaera_platera ep
            JOIN platera p ON ep.platera_id = p.id
            GROUP BY p.izena
        ");
        $data = $stmt->fetchAll(PDO::FETCH_ASSOC);
        echo json_encode($data);
        break;

    case 'dia_semana_mas_pedidos':
        $stmt = $pdo->query("
            SELECT DAYNAME(eskaeraOrdua) AS dia_semana, COUNT(*) AS total_pedidos
            FROM eskaera_platera
            GROUP BY dia_semana
            ORDER BY total_pedidos DESC
            LIMIT 1
        ");
        $data = $stmt->fetch(PDO::FETCH_ASSOC);
        echo json_encode($data);
        break;

    case 'dia_semana_mas_facturas':
        $stmt = $pdo->query("
            SELECT DAYNAME(eskaeraOrdua) AS dia_semana, COUNT(*) AS total_facturas
            FROM eskaera_platera
            WHERE egoera = 'entregado'
            GROUP BY dia_semana
            ORDER BY total_facturas DESC
            LIMIT 1
        ");
        $data = $stmt->fetch(PDO::FETCH_ASSOC);
        echo json_encode($data);
        break;

    case 'dia_mes_mas_pedidos':
        $stmt = $pdo->query("
            SELECT DAY(eskaeraOrdua) AS dia_mes, COUNT(*) AS total_pedidos
            FROM eskaera_platera
            GROUP BY dia_mes
            ORDER BY total_pedidos DESC
            LIMIT 1
        ");
        $data = $stmt->fetch(PDO::FETCH_ASSOC);
        echo json_encode($data);
        break;

    default:
        http_response_code(404);
        echo json_encode(['error' => 'Endpoint no encontrado']);
        break;
}
?>