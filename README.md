Engineering leader in enterprise integration — I take large IBM estates (ACE, MQ, MQFTE, DataStage, DataPower) and land them on Java, Spring Boot and Azure.

Thousands of interfaces and decades of middleware, moved without stopping the business — migration is an engineering problem, not a lift-and-shift.

Interested in agentic engineering: building CLI agents that do the discovery, the mapping and the grunt work so the humans do the judgement.

---

**"It's just one integration. Should take a sprint."**

```mermaid
flowchart LR
    A["System A"] ==> B["System B"]
```

**Two weeks later, in production:**

```mermaid
flowchart LR
    A["System A"] --> Q["MQ queue<br/>owner: unknown"]
    Q --> ACE["ACE flow<br/>last changed 2009"]
    ACE --> FTP["flat file<br/>on an FTP box"]
    FTP --> JCL["nightly batch<br/>02:00, do not ask"]
    JCL --> XLS["Dave's Excel macro"]
    XLS --> B["System B"]
    Q -.->|"retry storm"| Q
    XLS -.->|"Dave left in 2017"| GH["nobody knows"]
```

> This is why I do this for a living.

![Java](https://img.shields.io/badge/-Java-437291?style=flat-square&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/-Spring%20Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white)
![Micronaut](https://img.shields.io/badge/-Micronaut-000000?style=flat-square&logo=micronaut&logoColor=white)
![Azure](https://img.shields.io/badge/-Azure-0078D4?style=flat-square&logo=microsoftazure&logoColor=white)
![IBM MQ](https://img.shields.io/badge/-IBM%20MQ-052FAD?style=flat-square&logo=ibm&logoColor=white)
![Gradle](https://img.shields.io/badge/-Gradle-02303A?style=flat-square&logo=gradle&logoColor=white)
