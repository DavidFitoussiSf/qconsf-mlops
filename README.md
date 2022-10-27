## Introduction

This README contains instructions for local testing, deployment and cloud deployment of the news classification model.

## [Step 1] Download & Install Prerequisites:

### Create a local Python virtual environment, install Python dependencies

Before we can get started with writing any code for the project, we recommend creating a Python virtual environment. If you haven't created virtual environments in Python before, you can refer to [this documentation](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment). 

It needs the following steps (the commands shown below work for MacOS/Unix operating systems. Please refer to the documentation above for Windows):

1. Insall `pip`:
```bash 
$ python3 -m pip install --user --upgrade pip
```

2. Install `virtualenv`:
```bash
$ python3 -m pip install --user virtualenv
```

3. Create virtual environment: 
```bash
$ python3 -m venv mlopsproject
```

4. Activate the virtual environment:
```bash
$ source mlopsproject/bin/activate
```

5. Install the required python dependencies:
```bash
$ python3 -m pip install -r requirements.txt
```

go to the deploy/ directory and run:
```bash
$ python3 -m pip install -r requirements.txt
```

### Install Docker

Download and install Docker. You can follow the steps in [this document](https://docs.docker.com/get-docker/). 

If you are new to Docker, we suggest spending some time to get familiar with the Docker command line and dashboard. Docker's [getting started](https://docs.docker.com/get-started/) page is a good resource.

## [Step 2] Create a FastAPI web application to serve model predictions

1. Before getting started on the web application changes, make sure you have serialized the model artifact for deployment from Part1.ipynb. You can run the starter web server code:

```bash
$ cd deploy
$ uvicorn service:app --reload
```

You should see an output like:
```bash
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [29334] using watchgod
INFO:     Started server process [29336]
INFO:     Waiting for application startup.
2022-10-26 14:45:28.082 | INFO     | model.classifier:load:92 - Loaded trained model pipeline from: news_classifier.joblib
2022-10-26 14:45:31.705 | INFO     | service:startup_event:47 - Setup completed
INFO:     Application startup complete.
```

When you go to `http://127.0.0.1:8000` from a web browser, you should see this text output:
`{"Hello": "World"}`:


2. We are now ready to get started on writing the code! All the required code changes for this project are in `deploy/service.py`. Comments in this file will help you understand the changes we need to make to create our web application to make model predictions. Once the code changes are done, you can start the web server again using the command from the above step.

3. Test with an example request:

Visit `http://127.0.0.1:8000/docs`. You will see a /predict endpoint: 

![](https://corise-mlops.s3.us-west-2.amazonaws.com/project3/pic2.png)

You can click on "Try it now" which will let you modify the input request. Click on "Execute" to see the model prediction response from the web server:

![](https://corise-mlops.s3.us-west-2.amazonaws.com/project3/pic3.png)

Some suggested requests to try out: 

```bash
{
  "source": "BBC Technology",
  "url": "http://news.bbc.co.uk/go/click/rss/0.91/public/-/2/hi/business/4144939.stm",
  "title": "System gremlins resolved at HSBC",
  "description": "Computer glitches which led to chaos for HSBC customers on Monday are fixed, the High Street bank confirms."
}
```

```bash
{
  "source": "Yahoo World",
  "url": "http://us.rd.yahoo.com/dailynews/rss/world/*http://story.news.yahoo.com/news?tmpl=story2u=/nm/20050104/bs_nm/markets_stocks_us_europe_dc",
  "title": "Wall Street Set to Open Firmer (Reuters)",
  "description": "Reuters - Wall Street was set to start higher on\Tuesday to recoup some of the prior session's losses, though high-profile retailer Amazon.com  may come under\pressure after a broker downgrade."
}
```

```bash
{
  "source": "New York Times",
  "url": "",
  "title": "Weis chooses not to make pickoff",
  "description": "Bill Belichick won't have to worry about Charlie Weis raiding his coaching staff for Notre Dame. But we'll have to see whether new Miami Dolphins coach Nick Saban has an eye on any of his former assistants."
}
```

```bash
{
  "source": "Boston Globe",
  "url": "http://www.boston.com/business/articles/2005/01/04/mike_wallace_subpoenaed?rss_id=BostonGlobe--BusinessNews",
  "title": "Mike Wallace subpoenaed",
  "description": "Richard Scrushy once sat down to talk with 60 Minutes correspondent Mike Wallace about allegations that Scrushy started a huge fraud while chief executive of rehabilitation giant HealthSouth Corp. Now, Scrushy wants Wallace to do the talking."
}
```

```bash
{
  "source": "Reuters World",
  "url": "http://www.reuters.com/newsArticle.jhtml?type=worldNewsstoryID=7228962",
  "title": "Peru Arrests Siege Leader, to Storm Police Post",
  "description": "LIMA, Peru (Reuters) - Peruvian authorities arrested a former army major who led a three-day uprising in a southern  Andean town and will storm the police station where some of his  200 supporters remain unless they surrender soon, Prime  Minister Carlos Ferrero said on Tuesday."
}
```

```bash
{
  "source": "The Washington Post",
  "url": "http://www.washingtonpost.com/wp-dyn/articles/A46063-2005Jan3.html?nav=rss_sports",
  "title": "Ruffin Fills Key Role",
  "description": "With power forward Etan Thomas having missed the entire season, reserve forward Michael Ruffin has done well in taking his place."
}
```


## [Step 3] Containerize the application using Docker

Remember, we are containerizing this service to be deployed on AWS Lambda. There's a specific request schema that the API gateway will use to route the incoming request to the deployed lambda. We use Mangum (https://mangum.io/) to parse this request and spit out the json request that our endpoint can understand. 

1. Build the Docker Image
  
```bash

$ docker build --platform linux/amd64 -t news-classifier .
```

2. Start the container:

```bash

$ docker run -p 9000:8080 news-classifier:latest
```

3. Test the Docker container with an example request:

Execute the following example request from the command line: https://gist.github.com/nihit/6eabbc571a24fa0318b3893f4eaa6321

```bash

$ curl --location --request POST 'http://localhost:9000/2015-03-31/functions/function/invocations' \
--header 'Content-Type: application/json' \
--data-raw '{
    "resource": "/",
    "path": "/predict",
    "httpMethod": "POST",
    "headers": {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "cache-control": "no-cache",
        "CloudFront-Forwarded-Proto": "https",
        "CloudFront-Is-Desktop-Viewer": "true",
        "CloudFront-Is-Mobile-Viewer": "false",
        "CloudFront-Is-SmartTV-Viewer": "false",
        "CloudFront-Is-Tablet-Viewer": "false",
        "CloudFront-Viewer-Country": "US",
        "Content-Type": "application/json",
        "headerName": "headerValue",
        "Host": "gy415nuibc.execute-api.us-east-1.amazonaws.com",
        "Postman-Token": "9f583ef0-ed83-4a38-aef3-eb9ce3f7a57f",
        "User-Agent": "PostmanRuntime/2.4.5",
        "Via": "1.1 d98420743a69852491bbdea73f7680bd.cloudfront.net (CloudFront)",
        "X-Amz-Cf-Id": "pn-PWIJc6thYnZm5P0NMgOUglL1DYtl0gdeJky8tqsg8iS_sgsKD1A==",
        "X-Forwarded-For": "54.240.196.186, 54.182.214.83",
        "X-Forwarded-Port": "443",
        "X-Forwarded-Proto": "https"
    },
    "multiValueHeaders": {
        "Accept": [
            "*/*"
        ],
        "Accept-Encoding": [
            "gzip, deflate"
        ],
        "cache-control": [
            "no-cache"
        ],
        "CloudFront-Forwarded-Proto": [
            "https"
        ],
        "CloudFront-Is-Desktop-Viewer": [
            "true"
        ],
        "CloudFront-Is-Mobile-Viewer": [
            "false"
        ],
        "CloudFront-Is-SmartTV-Viewer": [
            "false"
        ],
        "CloudFront-Is-Tablet-Viewer": [
            "false"
        ],
        "CloudFront-Viewer-Country": [
            "US"
        ],
        "": [
            ""
        ],
        "Content-Type": [
            "application/json"
        ],
        "headerName": [
            "headerValue"
        ],
        "Host": [
            "gy415nuibc.execute-api.us-east-1.amazonaws.com"
        ],
        "Postman-Token": [
            "9f583ef0-ed83-4a38-aef3-eb9ce3f7a57f"
        ],
        "User-Agent": [
            "PostmanRuntime/2.4.5"
        ],
        "Via": [
            "1.1 d98420743a69852491bbdea73f7680bd.cloudfront.net (CloudFront)"
        ],
        "X-Amz-Cf-Id": [
            "pn-PWIJc6thYnZm5P0NMgOUglL1DYtl0gdeJky8tqsg8iS_sgsKD1A=="
        ],
        "X-Forwarded-For": [
            "54.240.196.186, 54.182.214.83"
        ],
        "X-Forwarded-Port": [
            "443"
        ],
        "X-Forwarded-Proto": [
            "https"
        ]
    },
    "queryStringParameters": {},
    "multiValueQueryStringParameters": {},
    "pathParameters": {},
    "stageVariables": {
        "stageVariableName": "stageVariableValue"
    },
    "requestContext": {
        "accountId": "12345678912",
        "resourceId": "roq9wj",
        "stage": "testStage",
        "requestId": "deef4878-7910-11e6-8f14-25afc3e9ae33",
        "identity": {
            "cognitoIdentityPoolId": null,
            "accountId": null,
            "cognitoIdentityId": null,
            "caller": null,
            "apiKey": null,
            "sourceIp": "192.168.196.186",
            "cognitoAuthenticationType": null,
            "cognitoAuthenticationProvider": null,
            "userArn": null,
            "userAgent": "PostmanRuntime/2.4.5",
            "user": null
        },
        "resourcePath": "/predict",
        "httpMethod": "POST",
        "apiId": "gy415nuibc"
    },
    "body": "{\"source\": \"\", \"url\": \"string\", \"title\": \"string\", \"description\": \"Ellis L. Marsalis Sr., the patriarch of a family of world famous jazz musicians, including grandson Wynton Marsalis, has died. He was 96.\"}",
    "isBase64Encoded": false
}'

```


## Deploying as serverless lambda

Once you have the Docker image, and have tested the container locally:

#### Create an ECR repository

![](https://corise-mlops.s3.us-west-2.amazonaws.com/qconsf/Screen+Shot+2022-10-26+at+4.29.28+PM.png)

#### Create the `lambda role` in IAM

![](https://corise-mlops.s3.us-west-2.amazonaws.com/qconsf/Screen+Shot+2022-10-26+at+5.03.17+PM.png)

#### Push Docker image and Update Lambda

[1] Login to the ECR repository
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 215673578938.dkr.ecr.us-west-2.amazonaws.com

[2] Push the Docker image to ECR:


```bash
docker tag news-classifier:latest 215673578938.dkr.ecr.us-west-2.amazonaws.com/news-classifier:latest

docker push 215673578938.dkr.ecr.us-west-2.amazonaws.com/news-classifier:latest
```

1. Create/Update lambda function: 


```bash
aws lambda create-function --function-name news-classifier-lambda --package-type Image --code ImageUri=215673578938.dkr.ecr.us-west-2.amazonaws.com/news-classifier:latest --role arn:aws:iam::215673578938:role/lambda-role --timeout 900--memory-size 2048
 ```

 Response:
 ```
 {
    "FunctionName": "news-classifier-lambda",
    "FunctionArn": "...",
    "Role": "...",
    "CodeSize": 0,
    "Description": "",
    "Timeout": 3,
    "MemorySize": 128,
    "LastModified": "2022-10-24T07:43:41.855+0000",
    "CodeSha256": "76e987507e09875d833208f21990d2543a36dbce5ff7db5935799effc6c94e1c",
    "Version": "$LATEST",
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "35be7fc5-ab9c-4ce7-9a57-46f40ed2cb34",
    "State": "Pending",
    "StateReason": "The function is being created.",
    "StateReasonCode": "Creating",
    "PackageType": "Image",
    "Architectures": [
        "x86_64"
    ]
}
```

We can now try executing the lambda in AWS console!


### Resources
Some good resources are:
* [Blog post](https://rafrasenberg.com/posts/deploying-fastapi-on-aws-as-a-lambda-container-image/) showing FastAPI deployment with API Gateway with a Dockerized Lambda
* [Another blog post](https://medium.com/analytics-vidhya/python-fastapi-and-aws-lambda-container-3e524c586f01) showing a similar deployment
* [AWS Docs](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html) for creating a Python Lambda with Docker

Future:
* [Blog post](https://radix.ai/blog/2020/12/swiftly-writing-and-deploying-apis-to-stay-agile/) showing Dockerized FastAPI with Fargate (and with Terraform) if we ever choose to move past Lambda

Other Docker commands that are useful:
* `docker ps`: Show list of running containers
* `docker images`: Show list of images available locally
* `docker images --digests`: Show list of images with the SHA256 digests of each image
* `docker container prune`: Delete stopped containers
* `docker rmi`: Delete an image
* `docker rmi -f $(docker images -aq)`: Delete all images
* `docker image prune`: Delete all dangling images
