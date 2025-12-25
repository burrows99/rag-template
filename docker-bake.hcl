group "default" {
  targets = ["retrieval-agent"]
}

target "retrieval-agent" {
  context = "./retrieval-agent-template"
  dockerfile = "Dockerfile"
  tags = ["langflow-agents/retrieval-agent:latest"]
}
