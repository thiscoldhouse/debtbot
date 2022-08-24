set -e

echo "Cloning fresh repo, this may require your git password\n"
cd /tmp
git clone https://github.com/thiscoldhouse/directactionbot.git
cd -
cp secrets.py /tmp/directactionbot/

# send the new artifact to the servers
echo "Sending deploy to $hostname"
rm -rf /tmp/directactionbot/.git
scp -r /tmp/directactionbot/ tad@tucker.ai:/tmp
rm -rf /tmp/directactionbot/
ssh -t tad@tucker.ai "
                   rm -rf /usr/src/directactionbot/* &&
                   mv /tmp/directactionbot/* /usr/src/directactionbot/ &&
                   rm -rf /tmp/directactionbot/ &&
                   /usr/src/venv/directactionbot/bin/pip install -r /usr/src/directactionbot/requirements.txt    &&
                   sudo /bin/systemctl daemon-reload &&
                   sudo /bin/systemctl restart directactionbot &&
                   sudo /bin/systemctl status directactionbot"
echo "Done"
