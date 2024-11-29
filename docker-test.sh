mkdir .testdata/data -p
mkdir .testdata/recordings -p

echo "Building Docker image"
docker image build -t freecorder .

echo "Running Docker image"
docker container run -p 5000:5000 -v $(pwd)/.testdata/data:/data -v $(pwd)/.testdata/recordings:/recordings --rm freecorder

echo "Cleaning up"
echo y | docker image prune
echo y | docker volume prune