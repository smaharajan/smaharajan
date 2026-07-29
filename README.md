Engineering leader in enterprise integration — I take large IBM estates (ACE, MQ, MQFTE, DataStage, DataPower) and land them on Java, Spring Boot and Azure.

Thousands of interfaces and decades of middleware, moved without stopping the business — migration is an engineering problem, not a lift-and-shift.

Interested in agentic engineering: building CLI agents that do the discovery, the mapping and the grunt work so the humans do the judgement.

---

### Expectation vs. Reality in Enterprise Integration

```mermaid
flowchart TD
    subgraph EXPECTATION["📋 What the Architecture Slide Promised"]
        direction LR
        A1["System A"] ===>|"Clean REST API (JSON)"| B1["System B"]
    end

    subgraph REALITY["🔥 What Actually Runs Production at 3 AM"]
        direction TB
        A2["System A"] -->|"1. CSV drop via SFTP"| B2["Unattended Windows VM"]
        B2 -->|"2. Secret Python 2.7 script"| C2["MQ Queue: DEV_TEST_FINAL_v2_PROD"]
        C2 -->|"3. Legacy ACE / IIB Flow"| D2["Mainframe JCL Batch Job"]
        D2 -->|"4. EBCDIC to ASCII magic"| E2["Database (Table: TEMP_FIX_2014)"]
        E2 -->|"5. Scheduled SQL Task"| F2["Bob's Excel Macro"]
        F2 -->|"6. Copy-Pasted into Web Form"| G2["System B"]

        F2 -.->|"Bob left 7 years ago"| CRASH["💥 Unknown Error -1"]
        C2 -.->|"Dead letter queue full"| CRASH
    end
```

![Java](https://img.shields.io/badge/-Java-437291?style=flat-square&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/-Spring%20Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white)
![Micronaut](https://img.shields.io/badge/-Micronaut-000000?style=flat-square&logo=micronaut&logoColor=white)
![Azure](https://img.shields.io/badge/-Azure-0078D4?style=flat-square&logo=microsoftazure&logoColor=white)
![IBM MQ](https://img.shields.io/badge/-IBM%20MQ-052FAD?style=flat-square&logo=ibm&logoColor=white)
![Gradle](https://img.shields.io/badge/-Gradle-02303A?style=flat-square&logo=gradle&logoColor=white)
