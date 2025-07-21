# Use an official Node.js runtime as a parent image
FROM node:14

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install any needed packages
RUN npm install

# Bundle app source
COPY . .

# Make port 3002 available to the world outside this container
EXPOSE 3002

# Run server.js when the container launches
CMD [ "node", "server.js" ]