# Module 1 Homework: Docker & SQL

In this homework we'll prepare the environment and practice
Docker and SQL

When submitting your homework, you will also need to include
a link to your GitHub repository or other public code-hosting
site.

This repository should contain the code for solving the homework. 

When your solution has SQL or shell commands and not code
(e.g. python files) file format, include them directly in
the README file of your repository.


## Question 1. Understanding docker first run 

Run docker with the `python:3.12.8` image in an interactive mode, use the entrypoint `bash`.

What's the version of `pip` in the image?

- **- 24.3.1**
- 24.2.1
- 23.3.1
- 23.2.1



## Solution for Question 1. Understanding docker first run

```
satiy@Satiyam MINGW64 ~/Downloads/data_engineering_zoomcamp/01-docker-terraform (main)
$ winpty docker run -it --entrypoint "bash" python:3.12.8
root@069120d01fbf:/# pip --version
pip 24.3.1 from /usr/local/lib/python3.12/site-packages/pip (python 3.12)
```




## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that **pgadmin** should use to connect to the postgres database?

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin  

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

- postgres:5433
- localhost:5432
- db:5433
- **- postgres:5432**
- **- db:5432**

If there are more than one answers, select only one of them



Download this data and put it into Postgres.

You can use the code from the course. It's up to you whether
you want to use Jupyter or a python script.

__Please refer to **load_green_taxi.ipynb** under **01-docker-terraform/2_docker_sql** for the loading through jupyter-notebook__


__Please refer to **load_green_taxi.py** under **01-docker-terraform/2_docker_sql** for the loading through python script__.


## Question 3. Trip Segmentation Count

During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, **respectively**, happened:
1. Up to 1 mile
2. In between 1 (exclusive) and 3 miles (inclusive),
3. In between 3 (exclusive) and 7 miles (inclusive),
4. In between 7 (exclusive) and 10 miles (inclusive),
5. Over 10 miles 

Answers:

- 104,802;  197,670;  110,612;  27,831;  35,281
- 104,802;  198,924;  109,603;  27,678;  35,189
- 104,793;  201,407;  110,612;  27,831;  35,281
- 104,793;  202,661;  109,603;  27,678;  35,189
- **- 104,838;  199,013;  109,645;  27,688;  35,202**


## Solution for Question 3. Trip Segmentation Count

```sql
-- question 3
SELECT 
	CASE
		WHEN trip_distance<=1 THEN 'UP_TO_1_MILE'
		WHEN trip_distance<=3 THEN 'UP_TO_3_MILE'
		WHEN trip_distance<=7 THEN 'UP_TO_7_MILE'
		WHEN trip_distance<=10 THEN 'UP_TO_10_MILE'
		ELSE '>10_MILE'
	END AS MILE_CLASSIFIER,
	COUNT(1)
FROM public.green_taxi_data
GROUP BY
CASE
	WHEN trip_distance<=1 THEN 'UP_TO_1_MILE'
	WHEN trip_distance<=3 THEN 'UP_TO_3_MILE'
	WHEN trip_distance<=7 THEN 'UP_TO_7_MILE'
	WHEN trip_distance<=10 THEN 'UP_TO_10_MILE'
	ELSE '>10_MILE'
END;
```


## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance?
Use the pick up time for your calculations.

Tip: For every day, we only care about one single trip with the longest distance. 

- 2019-10-11
- 2019-10-24
- 2019-10-26
- **- 2019-10-31**



## Solution for Question 4. Longest trip for each day

```sql
-- question 4
SELECT 
	TO_DATE(LEFT(lpep_pickup_datetime, 10), 'YYYY-MM-DD') lpep_pickup_date,
	MAX(trip_distance) MAX_DISTANCE_TRIP
FROM public.green_taxi_data
GROUP BY
	TO_DATE(LEFT(lpep_pickup_datetime, 10), 'YYYY-MM-DD')
ORDER BY MAX(trip_distance) DESC;
```



## Question 5. Three biggest pickup zones

Which were the top pickup locations with over 13,000 in
`total_amount` (across all trips) for 2019-10-18?

Consider only `lpep_pickup_datetime` when filtering by date.
 
- **- East Harlem North, East Harlem South, Morningside Heights**
- East Harlem North, Morningside Heights
- Morningside Heights, Astoria Park, East Harlem South
- Bedford, East Harlem North, Astoria Park


## Solution for Question 5. Three biggest pickup zones

```sql
--question 5
SELECT 
LEFT(gtt.lpep_pickup_datetime, 10) pickup_date,
gtt."PULocationID" "PULocationID",
lpu."Zone" pickup_location,
SUM(gtt.total_amount) total_amt
FROM public.green_taxi_data gtt
LEFT JOIN public.zones lpu ON gtt."PULocationID"=lpu."LocationID"
WHERE 
LEFT(gtt.lpep_pickup_datetime, 10)='2019-10-18' 
GROUP BY
LEFT(gtt.lpep_pickup_datetime, 10),
gtt."PULocationID",
lpu."Zone"
HAVING SUM(gtt.total_amount)>13000;
```



## Question 6. Largest tip

For the passengers picked up in October 2019 in the zone
named "East Harlem North" which was the drop off zone that had
the largest tip?

Note: it's `tip` , not `trip`

We need the name of the zone, not the ID.

- Yorkville West
- **- JFK Airport**
- East Harlem North
- East Harlem South


## Solution for Question 6. Largest tip

```sql
--Question 6
SELECT 
LEFT(gtt.lpep_pickup_datetime, 10) pickup_date,
pickup."Zone" pickup_location,
dropoff."Zone" dropoff_location,
gtt.tip_amount
FROM public.green_taxi_data gtt
LEFT JOIN public.zones pickup  ON gtt."PULocationID"=pickup."LocationID"
LEFT JOIN public.zones dropoff ON gtt."DOLocationID"=dropoff."LocationID"
WHERE
pickup."Zone"='East Harlem North'
ORDER BY tip_amount DESC;
```




## Terraform

In this section homework we'll prepare the environment by creating resources in GCP with Terraform.

In your VM on GCP/Laptop/GitHub Codespace install Terraform. 
Copy the files from the course repo
[here](../../../01-docker-terraform/1_terraform_gcp/terraform) to your VM/Laptop/GitHub Codespace.

Modify the files as necessary to create a GCP Bucket and Big Query Dataset.


__Comments from student:__
__Oracle Virtualbox environment was initialized for creation of terraform.__
__Refer to the **01-docker-terraform/1_terraform_gcp** for the initialization of terraform for:__
__- Terraform Basic__
__- Terraform with variables__



## Question 7. Terraform Workflow

Which of the following sequences, **respectively**, describes the workflow for: 
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform`

Answers:
- terraform import, terraform apply -y, terraform destroy
- teraform init, terraform plan -auto-apply, terraform rm
- terraform init, terraform run -auto-approve, terraform destroy
**- terraform init, terraform apply -auto-approve, terraform destroy**
- terraform import, terraform apply -y, terraform rm

