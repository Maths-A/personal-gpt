# Repo for school project to create a personal GPT server on kubernetes

The implenentation has been design to be cost-efficient by using only CPU and can be fully tested locally.

# Setup
## Run locally
### Llama server only
Run locally, go in the folder Repo/docker:
To start the server
`./start.sh`
To stop the server
`./stopt.sh`

### Local kubernetes
kubernets local deployment:
Start your kubernetes cluster from docker descktop.
In forder /kubernetes/local
`kubectl apply -f .`

### Remote cluster
#### Google cloud platform
Create an autopilot cluster (https://docs.cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview)
Connect to the cluster 
`gcloud container clusters get-credentials <your-project-name> --region <your-region> --project <project-ID>`
In forder /kubernetes/GCP
`kubectl apply -f .`
To know your public IP for your server:
`kubectl get svc -n personal-gpt`
Open the url: http://<service-url>:80

#### Nautilus
Change your kubectl config file in $HOME/.kube
Verify that you are in 
`kubectl config get-contexts`
Then setup your namespace 
`kubectl config set contexts.nautilus.namespace <YOUR-NAMESPACE>`
In forder /kubernetes/nautilus
`kubectl apply -f .`
`kubectl get ingress --watch`
Look at the hosts written for your ingress:
Open the url: http://<host-url>:80

## Technical choices
### Monitoring
For monitoring, I have used Helm librairy (https://www.youtube.com/watch?v=r45DkTMMouc)
I have deployed a Llama server with the Mistral Ai model 7b v0.1. I have tested this model with different quantizations: Q2, Q4.

### Autoscaling
I choose to based the autoscaling trigger on the cpu utilisation is over 80%, which increase a lot when we request the AI.

## Evaluation
### Performance test
For the evaluation, I have used grafana k6 librairy. This tools is an open-source load testing tool that allow developers and engineers test the performance and reliability of their systems.

I perform these test locally with a one node kubernetes cluster, on a MacBook Pro M4 Max with 128 Go. Each pods have 4 vCPU and 4 Go of Ram (up to 3 pods).

I have performed 4 types of test:
- **Load test:** Up to 5 looping VUs for 2m0s over 3 stages (gracefulRampDown: 30s, gracefulStop: 30s)
```markdown
| Quantizations         | Total request | Succeed request | Fail request | Average duration (s) | p(90)   | p(95)   |
|-----------------------|---------------|-----------------|--------------|----------------------|---------|---------|
| Q4 no auto-scale      | 40            | 40              | 0            | 25.98                | 32.36   | 32.53   |
| Q2                    | 44            | 44              | 0            | 21                   | 28.54   | 29.67   |
| Q4                    | 62            | 62              | 0            | 15.29                | 21      | 21.14   |
```
- **Stress test:** Up to 20 looping VUs for 3m0s over 4 stages (gracefulRampDown: 30s, gracefulStop: 30s)
```markdown
| Quantizations         | Total request | Succeed request | Fail request | Average duration (s) | p(90)   | p(95)   |
|-----------------------|---------------|-----------------|--------------|----------------------|---------|---------|
| Q4 no auto-scale      | 74            | 46              | 28           | 46.13                | >60     | >60     |
| Q2                    | 114           | 92              | 22           | 32.39                | >60     | >60     |
| Q4                    | 152           | 152             | 0            | 24.22                | 50.43   | 52.35   |
```
- **Spike test:** Up to 30 looping VUs for 50s over 3 stages (gracefulRampDown: 30s, gracefulStop: 30s)
```markdown
| Quantizations         | Total request | Succeed request | Fail request | Average duration (s) | p(90)   | p(95)   |
|-----------------------|---------------|-----------------|--------------|----------------------|---------|---------|
| Q4 no auto-scale      | 60            | 16              | 44           | 53.46                | 56.88   | 59.2    |
| Q2                    | 60            | 18              | 42           | 52.09                | >60     | >60     |
| Q4                    | 70            | 40              | 30           | 47.92                | >60     | >60     |
```
- **Soak test:** Up to 5 looping VUs for 12m0s over 3 stages (gracefulRampDown: 30s, gracefulStop: 30s)
```markdown
| Quantizations         | Total request | Succeed request | Fail request | Average duration (s) | p(90)   | p(95)   |
|-----------------------|---------------|-----------------|--------------|----------------------|---------|---------|
| Q4 no auto-scale      | 114           | 32              | 82           | 58.5                 | >60     | >60     |
| Q2                    | 464           | 464             | 0            | 13.47                | 16.3    | 16.51   |
| Q4                    | 384           | 384             | 0            | 26.57                | 32.76   | 35.41   |
```

### Cost
#### Google cloud platform (GCP)
The cost for running within GCP depend of the decided computation capacities. In my case, a configuration with 4 vCPU and 4 Go of Ram per pods (up to 3 pods). Cost arround 5$ the day.

#### Nautilus
Since Nautilus is free of charge, the cost evaluation is not applicable.