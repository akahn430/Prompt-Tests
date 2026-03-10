from setuptools import setup

setup(
    name="transcript-intent-router",
    version="0.1.0",
    py_modules=["app", "transcript_router"],
    install_requires=["openai>=1.40.0"],
    entry_points={
        "console_scripts": [
            "transcript-router=app:main",
        ]
    },
)
