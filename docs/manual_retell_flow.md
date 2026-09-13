# Manual Retell visual flow

Manual design documentation only. No Retell agent, workflow, state or tools have been created or modified.

NODE 00 global configuration applies throughout. Diagram is documentation, not a workflow import; complete edge conditions are in handoff_matrix.md.

```mermaid
flowchart TD
 START([Start]) --> N01[01 Greeting / Router]
 N01 --> N02[02 Texas License Guide]
 N01 --> N03[03 Adult Sales]
 N01 --> N04[04 Teen Sales]
 N01 --> N05[05 Road Test Sales]
 N01 --> N06[06 Booking]
 N01 --> N07[07 Student Support]
 N02 <--> N03
 N02 <--> N04
 N02 <--> N05
 N02 <--> N06
 N03 --> N06
 N04 --> N06
 N05 --> N06
 N06 <--> N07
 N06 --> N08[08 Human Escalation]
 N07 --> N08
 N02 --> N08
 N03 --> N08
 N04 --> N08
 N05 --> N08
 N01 --> N08
 N08 --> N09[09 End Call]
 N06 --> N09
 N07 --> N09
 N01 --> N09
```

Explicit changed goals reroute through 01 from specialists; temporary detours preserve shared context and revalidate slots on return. Human request takes priority. Demo confirmations stay synthetic; production-safe reads are provisional and writes go to staff. Diagram edges do not imply deployed APIs.
