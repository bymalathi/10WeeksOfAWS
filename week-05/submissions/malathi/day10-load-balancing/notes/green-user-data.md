#!/bin/bash

dnf install -y nginx

systemctl enable nginx
systemctl start nginx

cat > /usr/share/nginx/html/index.html <<'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>GREEN Environment</title>
    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            background: #dcfce7;
            font-family: Arial, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .page {
            width: 100%;
            min-height: 100vh;
            background: linear-gradient(135deg, #15803d, #4ade80);
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }

        .badge {
            background: white;
            color: #15803d;
            padding: 12px 25px;
            border-radius: 30px;
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 25px;
        }

        h1 {
            font-size: 60px;
            margin: 10px 0;
        }

        h2 {
            font-size: 28px;
            margin: 10px 0;
        }

        p {
            font-size: 20px;
            margin-top: 20px;
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
            GREEN DEPLOYMENT
        </div>

        <h1>🟢 GREEN ENVIRONMENT</h1>

        <h2>cloudadhar-day10-green</h2>

        <p>
            This is the Green application server.
        </p>

        <div class="server">
            Version: GREEN | Status: ACTIVE
        </div>

    </div>
</body>
</html>
EOF