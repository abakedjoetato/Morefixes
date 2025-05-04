{
  pname = "tower-of-temptation-discord-bot";
  version = "1.0.0";
  buildInputs = [
    pkgs.python311
    pkgs.python311Packages.discord-py
    pkgs.python311Packages.motor
    pkgs.python311Packages.pymongo
    pkgs.python311Packages.asyncssh
    pkgs.python311Packages.python-dotenv
  ];
}