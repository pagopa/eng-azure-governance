# Pattern Selection Map

Load this file when you know the design pressure but have not chosen the right pattern yet.

| Pressure | Prefer | Good fit when | Avoid when |
| --- | --- | --- | --- |
| Construction is repetitive or invalid intermediate states are common | Builder | Call sites are noisy or order matters | The object has only a few obvious required fields |
| Callers should not know which concrete class to instantiate | Factory Method | The concrete implementation varies by environment, feature, or subtype | A single constructor is stable and readable |
| One behavior branch keeps growing | Strategy | Variants are independently testable and likely to expand | There are only two stable branches with no expected growth |
| Behavior changes by internal lifecycle phase | State | State transitions are explicit and behavior differs materially by state | The "state" is just one flag with trivial branching |
| A foreign API shape leaks into the core model | Adapter | The incompatibility is local to one boundary | The whole subsystem should be hidden behind a simpler entry point |
| A subsystem is too chatty or hard to enter | Facade | Clients need one simpler boundary | Clients still need fine-grained subsystem control |
| Optional behavior layers keep multiplying | Decorator | Features should compose dynamically around one contract | Behavior can be expressed with one focused collaborator |
| Access, remote calls, caching, or lazy loading need a stand-in | Proxy | Clients should keep the same surface while access is controlled | The wrapper would mostly rename methods without adding behavior |
| Many listeners must react to one source | Observer | Fan-out and loose coupling matter | A direct call chain is simpler and stable |
| Peer objects are tightly coordinating in many directions | Mediator | One coordinator can simplify the collaboration graph | The workflow is simple enough for direct calls |

## Anti-Triggers

- Prefer a plain function or module when there is no long-lived object state.
- Prefer a data table or mapping when behavior selection is declarative.
- Prefer composition before inheritance for code reuse.
- Prefer removing accidental responsibilities from a god class before adding new abstractions around it.
