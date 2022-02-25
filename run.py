from fastapi import FastAPI
import uvicorn
from main import application



app = FastAPI(
    title='BDSF by spiritlhl',
    description='为偷塔而生',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redocs',
)

#prefix后缀地址
app.include_router(application, prefix='/tt', tags=['basic'])

# 运行
if __name__ == '__main__':
    uvicorn.run('run:app', host='0.0.0.0', port=7788, debug=True, workers=1)# reload=True,
