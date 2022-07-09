# Application

## How to Use

### Docker

```console
$ docker compose build
$ docker compose up -d app
```

### Singularity

```console
$ singularity build -f singularity/image.sif singularity/env.def
$ singularity instance start singularity/image.sif kagari
```

## 構成

modelディレクトリには対話システムの中核となるもの（例えばロジックなど）を書いていく。  
viewディレクトリにはclient.pyがあり、これを実行することで対話システムが起動する。

```
/app
├── README.md
├── model
└── view
    └── client.py
```
