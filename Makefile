.PHONY: help setup clean install-backend install-frontend start-backend start-frontend dev build

# 默认目标
help: ## 显示帮助信息
	@echo "AutoTest Hub 可用命令："
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## 初始化项目
	pip install -r backend/requirements.txt
	cd frontend && npm install
	@echo "项目初始化完成！"

install-backend: ## 安装后端依赖
	cd backend && pip install -r requirements.txt

install-frontend: ## 安装前端依赖
	cd frontend && npm install

start-backend: ## 启动后端服务
	cd backend && python main.py

start-frontend: ## 启动前端服务
	cd frontend && npm run dev

dev: ## 启动开发环境（前后端）
	@echo "启动后端服务..."
	cd backend && python main.py &
	@echo "启动前端服务..."
	cd frontend && npm run dev

build: ## 打包 Electron 应用
	cd frontend && npm run electron:build

clean: ## 清理临时文件
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf reports/
	rm -rf backend/data/
	rm -rf backend/logs/
	rm -rf frontend/node_modules/
	rm -rf frontend/dist/
	rm -rf frontend/release/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
