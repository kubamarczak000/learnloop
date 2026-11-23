"""Public, read-only GraphQL data for the personal portfolio."""

from graphql import (
    GraphQLBoolean,
    GraphQLField,
    GraphQLList,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLString,
)


ProjectType = GraphQLObjectType(
    "Project",
    {
        "name": GraphQLField(GraphQLString),
        "description": GraphQLField(GraphQLString),
        "category": GraphQLField(GraphQLString),
        "stack": GraphQLField(GraphQLList(GraphQLString)),
        "demoUrl": GraphQLField(GraphQLString),
        "sourceUrl": GraphQLField(GraphQLString),
        "screenshotUrl": GraphQLField(GraphQLString),
        "status": GraphQLField(GraphQLString),
        "featured": GraphQLField(GraphQLBoolean),
    },
)

ContactType = GraphQLObjectType(
    "ContactLinks",
    {
        "github": GraphQLField(GraphQLString),
        "linkedin": GraphQLField(GraphQLString),
    },
)

PortfolioType = GraphQLObjectType(
    "Portfolio",
    {
        "headline": GraphQLField(GraphQLString),
        "intro": GraphQLField(GraphQLString),
        "projects": GraphQLField(GraphQLList(ProjectType)),
        "skills": GraphQLField(GraphQLList(GraphQLString)),
        "contact": GraphQLField(ContactType),
    },
)

PORTFOLIO = {
    "headline": "Buduję aplikacje webowe w Pythonie.",
    "intro": (
        "Tworzę praktyczne projekty, rozwijam swoje umiejętności i poznaję nowe "
        "technologie. Tutaj zbieram aplikacje i pomysły, nad którymi pracuję."
    ),
    "projects": [
        {
            "name": "LearnLoop",
            "description": (
                "Planer nauki i pracy. Pomaga organizować zadania, cele, sesje nauki "
                "i ważne daty w kalendarzu."
            ),
            "category": "Aplikacja webowa",
            "stack": ["Python", "Flask", "SQLite"],
            "demoUrl": "https://learnloop-production-bfea.up.railway.app/login",
            "sourceUrl": "https://github.com/kubamarczak000/learnloop",
            "screenshotUrl": "/static/images/learnloop-dashboard.png",
            "status": "live",
            "featured": True,
        },
        {"name": "SOC Threat Detection Platform", "stack": ["Python", "SQL"], "status": "building"},
        {"name": "Linux System Security Monitor", "stack": ["Linux"], "status": "building"},
        {"name": "Network Traffic Investigation", "stack": ["Wireshark", "Networking"], "status": "building"},
        {"name": "Home SOC Lab", "stack": ["Wazuh", "Windows", "Linux"], "status": "building"},
        {"name": "File Integrity Monitor", "stack": ["Python", "C", "SHA-256"], "status": "building"},
        {"name": "Web Application Security Lab", "stack": ["Java", "Node", "Burp", "OWASP"], "status": "building"},
        {"name": "Threat Intelligence Analyzer", "stack": ["Python", "APIs", "JSON"], "status": "building"},
        {"name": "Secure Authentication System", "stack": ["Java", "MySQL"], "status": "building"},
        {"name": "OWASP Web Security Lab", "stack": ["OWASP", "Burp Suite"], "status": "building"},
        {"name": "Incident Response Case Study", "stack": ["MITRE", "Incident Response"], "status": "building"},
        {"name": "Cloud Security Lab", "stack": ["Cloud", "IAM", "Security"], "status": "building"},
    ],
    "skills": ["Python", "Flask", "GraphQL", "React", "Bootstrap", "SQLite", "Git"],
    "contact": {
        "github": "https://github.com/kubamarczak000",
        "linkedin": "https://www.linkedin.com/in/jakub-marczak-b28aa33b7/",
    },
}

QueryType = GraphQLObjectType(
    "Query",
    {"portfolio": GraphQLField(PortfolioType, resolve=lambda _root, _info: PORTFOLIO)},
)

schema = GraphQLSchema(query=QueryType)
