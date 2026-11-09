# Punto 3 · Diagrama de la revisión

La propuesta tal como está escrita, con mis comentarios marcados: no es una arquitectura alternativa.
Los números entre paréntesis son los componentes de la propuesta; los códigos (a1, b2, c1, d1...) son
los del [reporte](../REPORTE.md).

- **Rojo:** lo que no aplica o se rompe (a, b).
- **Ámbar:** lo que falta (c), cuando tiene un lugar claro. c2, c4, c5 y c6 afectan a todo el sistema y
  están solo en el reporte.
- **Verde:** lo que rescataría (d).

Las notas tienen bordes redondeados; los componentes de la propuesta son rectángulos.

Imagen exportada: [diagram.png](diagram.png).

```mermaid
%%{init: {"flowchart": {"wrappingWidth": 400}}}%%
flowchart LR
    subgraph entrada["ENTRADA · ERP del cliente → Fracttal"]
        erp2["ERP del cliente"]
        hook["Webhook HTTPS (4)"]
        yaml["Motor de transformación<br/>en YAML (5)"]
        db[("Base de datos (2)<br/>propuesta: una por cliente<br/>contexto: una compartida")]
        events[("Tabla de eventos (8)<br/>payload completo")]
        erp2 -- "llama" --> hook
        hook --> yaml
        yaml -- "escribe" --> db
        hook -- "guarda" --> events
        hook -. "200 solo al terminar" .-> erp2

        c3("c3 · falta: ¿y los ERPs que no pueden<br/>llamarnos (on-premise)?"):::missing
        b1("b1 · si tarda más que el timeout,<br/>el ERP reenvía y el dato se duplica"):::problem
        c1("c1 · falta: ¿cómo se autentica el ERP<br/>y de dónde sale el cliente?"):::missing
        d1("d1 · eventos donde el ERP lo permita"):::rescue
        a1("a1 · una base por cliente choca con el contexto;<br/>un esquema por cliente no escala por separado"):::problem
        d2y("d2 · reduce el código a medida,<br/>no lo elimina"):::rescue
        d4("d4 · sí, pero con los payloads fuera<br/>de la base compartida (S3), con retención"):::rescue
        erp2 -.- c3
        hook -.- b1
        hook -.- c1
        hook -.- d1
        db -.- a1
        yaml -.- d2y
        events -.- d4
    end

    subgraph salida["SALIDA · Fracttal → ERP del cliente"]
        op["Operación en Fracttal<br/>(orden de trabajo, activo, lectura)"]
        kafka[["Kafka (1)"]]
        subgraph svc["d2 · Microservicio por ERP (3), p. ej. SAP: se rescata"]
            wA["Worker cliente A (3)<br/>token en memoria (7)"]
            wB["Worker cliente B (3)<br/>token en memoria (7)"]
        end
        erp1["ERP del cliente"]
        op -- "publica evento" --> kafka
        kafka --> wA
        kafka --> wB
        wA -- "reintenta hasta<br/>que responda (6)" --> erp1
        wB --> erp1

        d3("d3 · el bus sí; Kafka según las cifras (c5)"):::rescue
        a2("a2 · se separa la CPU, pero la base es la misma;<br/>cada cliente es un proceso más que operar"):::problem
        b3("b3 · un token por réplica: 401 en cascada"):::problem
        b2("b2 · sin límite: el cliente queda atascado<br/>y se pueden duplicar órdenes"):::problem
        kafka -.- d3
        wA -.- a2
        wB -.- b3
        erp1 -.- b2
    end

    classDef problem fill:#fdecea,stroke:#c0392b,color:#7b241c
    classDef missing fill:#fff4e0,stroke:#d68910,color:#7e5109
    classDef rescue fill:#e9f7ef,stroke:#1e8449,color:#145a32
    style svc fill:#e9f7ef,stroke:#1e8449,color:#145a32
    style entrada fill:#f6f6f6,stroke:#999999
    style salida fill:#f6f6f6,stroke:#999999
```
