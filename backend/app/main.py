import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import (
    auth, users, production, safety, equipment,
    laboratory, report, energy, document, material,
    performance, system
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="污水处理厂智能管理系统",
    description="Water Treatment Plant Intelligent Management System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(production.router)
app.include_router(safety.router)
app.include_router(equipment.router)
app.include_router(laboratory.router)
app.include_router(report.router)
app.include_router(energy.router)
app.include_router(document.router)
app.include_router(material.router)
app.include_router(performance.router)
app.include_router(system.router)


@app.get("/")
def root():
    return {
        "message": "污水处理厂智能管理系统 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/dashboard/overview")
def get_dashboard_overview():
    """首页仪表盘概览数据"""
    return {
        "water_treatment": {
            "today_intake": 15200,
            "today_output": 14800,
            "processing_rate": 97.4,
            "unit": "m³"
        },
        "water_quality": {
            "cod_inlet": 185,
            "cod_outlet": 28,
            "cod_removal_rate": 84.9,
            "nh3n_inlet": 38,
            "nh3n_outlet": 3.5,
            "nh3n_removal_rate": 90.8
        },
        "equipment": {
            "total": 156,
            "running": 142,
            "maintenance": 8,
            "fault": 6,
            "running_rate": 91.0
        },
        "alarms": {
            "total_today": 12,
            "urgent": 2,
            "warning": 5,
            "normal": 5,
            "unhandled": 3
        },
        "energy": {
            "today_power": 12580,
            "yesterday_power": 12850,
            "power_unit": "kWh",
            "today_cost": 8806,
            "month_cost": 285000,
            "cost_unit": "元"
        },
        "tasks": {
            "inspection_pending": 5,
            "maintenance_pending": 8,
            "detection_pending": 12
        }
    }


@app.get("/api/dashboard/trends")
def get_dashboard_trends():
    """获取趋势数据"""
    return {
        "water_volume": {
            "labels": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
            "intake": [580, 520, 680, 720, 700, 650],
            "output": [560, 500, 660, 700, 680, 630]
        },
        "water_quality": {
            "labels": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            "cod": [28, 26, 30, 25, 27, 29, 28],
            "nh3n": [3.5, 3.2, 3.8, 3.1, 3.4, 3.6, 3.5]
        },
        "energy": {
            "labels": ["1月", "2月", "3月", "4月", "5月", "6月"],
            "consumption": [380000, 350000, 365000, 375000, 390000, 385000],
            "cost": [266000, 245000, 255500, 262500, 273000, 269500]
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
