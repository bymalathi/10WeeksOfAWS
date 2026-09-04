#!/bin/bash

dnf install -y nginx

systemctl enable nginx
systemctl start nginx

cat > /usr/share/nginx/html/index.html <<'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>BLUE Environment</title>
    <style>
        * {
            box-sizing: border-box;
        }

        html, body {
            margin: 0;
            width: 100%;
            height: 100%;
            font-family: Arial, sans-serif;
        }

        .page {
            width: 100%;
            min-height: 100vh;
            background: linear-gradient(135deg, #1d4ed8, #60a5fa);
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }

        .badge {
            background: white;
            color: #1d4ed8;
            padding: 12px 30px;
            border-radius: 30px;
            font-weight: bold;
            font-size: 18px;
        }

        h1 {
            font-size: 60px;
            margin: 25px 0 10px;
        }

        h2 {
            font-size: 30px;
            margin: 10px 0;
        }

        p {
            font-size: 20px;
        }

        .server {
            margin-top: 30px;
            padding: 15px 30px;
            border: 2px solid white;
            border-radius: 10px;
            font-size: 18px;
        }
    </style>
</head>

<body>
    <div class="page">

        <div class="badge">
            BLUE DEPLOYMENT
        </div>

        <h1>BLUE ENVIRONMENT</h1>

        <h2>cloudadhar-day10-blue</h2>

        <p>This is the Blue application server.</p>

        <div class="server">
            Version: BLUE | Status: ACTIVE
        </div>

    </div>
</body>
</html>
EOF