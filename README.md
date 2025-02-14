This is my genetic boids project. Its boids with genes mixed in. All boids are created with a random lifespan, and when they die, 2 new boids are created. They inheret their parents genes in the form of the exact rgv values that the parent had.
Then some random genetic drift is applied to the color, with a bias towards the color they already are in, in the form of a genetic marker. If their color drifts too far, their genetic marker changes. Boids only flock with boids of the same
genetic marker. They get bigger as they age, and they die if the get separated from the flock. It creates some very beautiful boids

This boid simulation contains some pretty cool optimizations. You will notice the area is split into sectors. Boids only check for nearby boids by looking at what boids are in its sector, and adjacent sectors.

This is 1,000 boids! And I managed to keep the operations around or under 30k! Given that 1000 boids in a nested loop would be 1,000,000 operations, this is amazing!
![image](https://github.com/user-attachments/assets/4b3b5ad5-0230-480a-82d9-faa36bb0fde0)


They like to spiral in large numbers, a problem I've tried hard to fix. 
![image](https://github.com/user-attachments/assets/9c78fe88-e541-49c6-b347-feb5fbba5e3e)

![image](https://github.com/user-attachments/assets/0a418ab0-33d3-49e4-8b0f-3e18c568cd8c)

![image](https://github.com/user-attachments/assets/b33f3d9d-5c36-4370-acce-cb91c4920ece)




