from typing_extensions import NotRequired, TypedDict


class ValidationQuestion(TypedDict):
    id: str
    course_id: str
    question: str

    must_include: NotRequired[list[str]]
    must_not_include: NotRequired[list[str]]
    expected_sources: NotRequired[list[str]]
    description: NotRequired[str]


QUESTIONS: list[ValidationQuestion] = [

    {
        "id": "1",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "list two different firewall types",
        "must_include": [
            "packet filtering",
            "stateful inspection",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "expected_sources": [
            "Firewall (1).pdf",
        ],
        "description": "Should name the two firewall types from the firewall PDF.",
    },
    {
        "id": "2",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what room is the final exam in",
        "must_include": [
            "course material"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should indicate that the answer is not available from the course material rather than using the old strict no-answer response."
    },
    {
        "id": "3",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what does a packet filtering firewall do",
        "must_include": [
            "packet",
            "header",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should describe how packet filtering firewall works at a basic level.",
    },
    {
        "id": "4",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is stateful inspection firewall",
        "must_include": [
            "state",
            "connection",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should explain that stateful firewall tracks connection state.",
    },
    {
        "id": "5",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the difference between packet filtering and stateful inspection firewalls",
        "must_include": [
            "packet"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should explain that packet filtering checks headers, while stateful inspection tracks active connections and may inspect more context.",
    },
    
    {
        "id": "6",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what does EVE stand for",
        "must_include": [
            "extraction",
            "validation",
            "enumeration",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should expand the EVE acronym correctly.",
    },
    {
        "id": "7",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what are the three stages of the EVE framework",
        "must_include": [
            "exhaust",
            "validation",
            "enumeration",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should list the three stages of EVE.",
    },
    {
        "id": "8",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "why does RAG fail to guarantee completeness",
        "must_include": [
            "top",
            "k",
            "retrieval",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should mention limitation of top-k retrieval and missing information.",
    },
    {
        "id": "9",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the purpose of the validation stage in EVE",
        "must_include": [
            "false positive",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should explain validation removes incorrect candidates.",
    },
    {
        "id": "10",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is one limitation of EVE",
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should mention limitation due to natural language ambiguity.",
    },

    {
        "id": "11",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "who is the instructor of the course",
        "must_include": [
            "mohamed",
            "selim",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should correctly identify the instructor.",
    },
    {
        "id": "12",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "where is the lecture held",
        "must_include": [
            "hall",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should extract lecture location.",
    },
    {
        "id": "13",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what are all the available office hours",
        "must_include": [
            "10:30",
            "11:30",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should extract office hours time.",
    },
    {
        "id": "14",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what textbook is used in this course",
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should indicate textbook info is not available in course material since no textbook is mentioned in any course document. Correct path is C.",
    },
    {
        "id": "15",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "where is the instructor's office located",
        "must_include": [
            "305",
            "Durham"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should extract instructor office location."
    },

    {
        "id": "16",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the internship term",
        "must_include": [
            "summer",
            "2026",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should extract internship term.",
    },
    {
    "id": "21",
    "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
    "question": "what degree programs are preferred for this internship",
    "must_include": [
        "computer science",
        "computer engineering"
    ],
    "must_not_include": [
        "chunk",
        "metadata",
        "retrieved materials",
        "based on general knowledge"
    ],
    "description": "Should mention computer science or computer engineering as preferred degree programs, based on course material, without using general knowledge fallback."
    },
    {
        "id": "18",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "name one programming language preferred for this role",
        "must_include": [
            "python",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should include Python (or Go).",
    },
    {
        "id": "19",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is one responsibility of this internship",
        "must_include": [
            "code",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should mention coding/testing/debugging responsibility.",
    },
    {
        "id": "20",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the salary for this internship",
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should say the salary is not available in the provided course material, without guessing or giving extra advice."
    },

    {
        "id": "21",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "when is the final exam",
        "must_include": [
            "may",
            "13"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should extract final exam date from schedule."
    },
    {
        "id": "22",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what time is the final exam",
        "must_include": [
            "9:45",
            "11:45"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should extract final exam time range."
    },
    {
        "id": "23",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what topic is covered on march 31",
        "must_include": [
            "host-based firewalls"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should identify the topics covered on March 31 from the schedule."
    },
    {
        "id": "24",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what topic is covered on february 17",
        "must_include": [
            "firewalls"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should identify topic for that lecture date."
    },
    {
        "id": "25",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "when is homework 1 due",
        "must_include": [
            "02/04",
            "11:59"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should extract HW 01 due date and time."
    },

    {
        "id": "26",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the purpose of a firewall",
        "must_include": [
            "protect",
            "network"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should explain firewall protects internal network from external threats."
    },
    {
        "id": "27",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the difference between packet filtering and stateful firewalls",
        "must_include": [
            "stateless",
            "state"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should explain stateless vs stateful behavior and connection tracking."
    },
    {
        "id": "28",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what does iptables do in linux",
        "must_include": [
            "user",
            "rules"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should describe iptables as user-space tool to manage netfilter rules."
    },
    {
        "id": "29",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what command is used to drop icmp packets in iptables",
        "must_include": [
            "iptables",
            "icmp",
            "DROP"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should include iptables command dropping ICMP packets."
    },
    {
        "id": "30",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what does a firewall use to decide whether to allow or block traffic",
        "must_include": [
            "packet"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should explain that firewalls use rules based on packet information to allow or block traffic."
    },

    {
        "id": "31",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is pfSense",
        "must_include": [
            "firewall",
            "freebsd"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should describe pfSense as open-source firewall/router based on FreeBSD."
    },
    {
        "id": "32",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "where should a firewall be deployed in a large organization",
        "must_include": [
            "network",
            "boundaries"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should explain firewall placement at network boundaries or entry points."
    },
    {
        "id": "33",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the default deny policy in firewalls",
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should explain default deny drops packets when no rule matches."
    },
    {
        "id": "34",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what information does a packet filtering firewall use to make decisions",
        "must_include": [
            "ip",
            "port",
            "protocol"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should list packet attributes such as IP address, port number, and protocol."
    },
    {
        "id": "35",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what encryption algorithm does pfSense use",
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should state that the encryption algorithm is not available in the course material without guessing or using general knowledge."
    },

    {
        "id": "36",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the main difference between tcp and udp",
        "must_include": [
            "connection",
            "reliable"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should explain TCP is connection-oriented and reliable while UDP is connectionless and not reliable."
    },
    {
        "id": "37",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is a port in networking",
        "must_include": [
            "application",
            "service"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should describe port as a location associated with a service or application."
    },
    {
        "id": "38",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the range of well known ports",
        "must_include": [
            "0",
            "1023"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should state that well-known ports range from 0 to 1023."
    },
    {
        "id": "39",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the purpose of the tcp three way handshake",
        "must_include": [
            "connection",
            "establish"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should explain that the three-way handshake establishes a TCP connection."
    },
    {
        "id": "40",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what port does ftp use",
        "must_include": [
            "20",
            "21"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should state that FTP uses port 21 for control and port 20 for data."
    },

    {
        "id": "41",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what does the fisherman do in his free time",
        "must_include": [
            "sleep",
            "guitar",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should describe how the fisherman spends his free time.",
    },
    {
        "id": "42",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "why does the fisherman not catch more fish",
        "must_include": [
            "enough",
            "family",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should explain that the fisherman only catches enough to support his needs.",
    },
    {
        "id": "43",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what kind of fish did the fisherman catch",
        "must_include": [
            "tuna"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials"
        ],
        "description": "Should identify the type of fish caught by the fisherman.",
    },
    {
        "id": "44",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "how long did the businessman say the plan would take",
        "must_include": [
            "15",
            "20",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should mention the estimated timeline given by the businessman.",
    },
    {
        "id": "45",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what company did the fisherman work for",
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should refuse because the fisherman's employer is not mentioned in the materials.",
    },

    {
        "id": "46",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is one difference between an array and an arraylist",
        "must_include": [
            "fixed size",
            "dynamic"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should explain that arrays have fixed size while ArrayLists are dynamic.",
    },
    {
        "id": "47",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what can arraylists store when working with primitive values",
        "must_include": [
            "primitive",
            "wrapper"
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should explain that ArrayLists store objects and use wrapper classes for primitive values.",
    },
    {
        "id": "48",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what are the four components of oop",
        "must_include": [
            "encapsulation",
            "inheritance",
            "polymorphism",
            "abstraction",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should list the four main components of object oriented programming.",
    },
    {
        "id": "49",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is a class and what is an object",
        "must_include": [
            "blueprint",
            "instance",
        ],
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should explain that a class is a blueprint and an object is an instance of a class.",
    },
    {
        "id": "50",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the time complexity of binary search",
        "must_not_include": [
            "chunk",
            "metadata",
            "retrieved materials",
        ],
        "description": "Should refuse because binary search complexity is not mentioned in the materials.",
    },
<<<<<<< Updated upstream
  
=======
    {
        "id": "51",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the main purpose of a firewall in a network",
        "must_include": ["protect", "network"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should explain firewall protects network from threats."
    },
    {
        "id": "52",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "where should a firewall be placed in a large organization",
        "must_include": ["network", "boundaries"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should mention deployment at network boundaries."
    },
    {
        "id": "53",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what happens when no firewall rule matches a packet",
        "must_include": ["default", "deny", "drop"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should explain default deny policy."
    },
    {
        "id": "54",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what attributes of a packet are used in firewall rules",
        "must_include": ["ip", "port", "protocol"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should mention IP, port, and protocol."
    },
    {
        "id": "55",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is pfSense",
        "must_include": ["firewall", "freebsd"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should describe pfSense as firewall/router software."
    },
    {
        "id": "56",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the main difference between tcp and udp",
        "must_include": ["connection", "reliable"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should explain TCP reliable vs UDP connectionless."
    },
    {
        "id": "57",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the purpose of the tcp three way handshake",
        "must_include": ["connection", "establish"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should explain handshake establishes connection."
    },
    {
        "id": "58",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what does a port represent in networking",
        "must_include": ["application", "service"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should explain port as service endpoint."
    },
    {
        "id": "59",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the range of well known ports",
        "must_include": ["0", "1023"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should state range 0-1023."
    },
    {
        "id": "60",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "does udp guarantee delivery of packets",
        "must_include": ["no", "not", "guarantee"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should clearly state UDP is unreliable."
    },
    {
        "id": "61",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "when is the midterm exam",
        "must_include": ["march", "5"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should extract midterm date."
    },
    {
        "id": "62",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what topic is covered on february 24",
        "must_include": ["dns", "routing"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should extract lecture topics."
    },
    {
        "id": "63",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "when is homework 3 due",
        "must_include": ["3/11", "11:59"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should extract HW3 due date."
    },
    {
        "id": "64",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what happens during week 8 of the course",
        "must_include": ["spring break"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should identify spring break."
    },
    {
        "id": "65",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "where is the final exam held",
        "expected_exact": "I do not have enough course information to answer that.",
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should refuse because location is not mentioned."
    },
    {
        "id": "66",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "where was the fisherman located",
        "must_include": ["mexican", "village"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should mention small Mexican coastal village."
    },
    {
        "id": "67",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what did the fisherman catch",
        "must_include": ["tuna"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should identify yellow-fin tuna."
    },
    {
        "id": "68",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "why did the fisherman not want to catch more fish",
        "must_include": ["enough", "family"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should explain he had enough for his needs."
    },
    {
        "id": "69",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what did the businessman suggest the fisherman should do",
        "must_include": ["business", "boats"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should describe expansion plan."
    },
    {
        "id": "70",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is the main idea of the story",
        "must_include": ["life", "simple"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should capture theme of simple life vs ambition."
    },
    {
        "id": "71",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is one difference between arrays and arraylists",
        "must_include": ["fixed", "dynamic"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should explain fixed vs dynamic size."
    },
    {
        "id": "72",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what can arraylists store when using primitive values",
        "must_include": ["wrapper", "object"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should explain wrapper classes."
    },
    {
        "id": "73",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what are the four components of oop",
        "must_include": ["encapsulation", "inheritance", "polymorphism", "abstraction"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should list all OOP pillars."
    },
    {
        "id": "74",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is a class in java",
        "must_include": ["blueprint"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should describe class as blueprint."
    },
    {
        "id": "75",
        "course_id": "0a73951d-7475-44c4-889a-d146c849cce3",
        "question": "what is an object in java",
        "must_include": ["instance"],
        "must_not_include": ["chunk", "metadata", "retrieved materials"],
        "description": "Should describe object as instance of class."
    },

>>>>>>> Stashed changes
]