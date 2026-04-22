.PHONY: help start stop restart logs config

help:
	@echo "NexusKB 快速命令"
	@echo "  make start   - 一键启动所有服务"
	@echo "  make stop    - 停止所有服务"
	@echo "  make restart - 重启所有服务"
	@echo "  make logs    - 查看日志"
	@echo "  make config  - 校验 docker compose 配置"

start:
	docker compose up -d --build
	@echo "NexusKB 已启动"
	@echo "前端: http://localhost:11420"
	@echo "后端: http://localhost:16088"

stop:
	docker compose down

restart:
	docker compose down
	docker compose up -d --build

logs:
	docker compose logs -f

config:
	docker compose config
