{ pkgs }:

{
  deps = [
    pkgs.python310
    pkgs.python310Packages.discord-py
    pkgs.python310Packages.motor
    pkgs.python310Packages.pymongo
    pkgs.python310Packages.python-dotenv
    pkgs.python310Packages.asyncssh
    pkgs.python310Packages.aiohttp
    pkgs.python310Packages.pillow
  ];
  
  env = {
    PYTHONUNBUFFERED = "1";
    PYTHONPATH = ".";
  };
}