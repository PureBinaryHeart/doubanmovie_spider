from setuptools import setup, find_packages
setup(
      name="doubanmovie",
      version="0.1",
      description="a spider for actor information in douban.com",
      author="Ruodai Cui",
      url="https://github.com/PureBinaryHeart",
      license="MIT",
      packages= find_packages(),
      scripts=["/root/spider/test.py"],
      )
