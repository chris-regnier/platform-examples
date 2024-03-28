package test

import (
	"fmt"
	"os"
	"testing"

	"os/exec"

	"github.com/gruntwork-io/terratest/modules/docker"
	"github.com/gruntwork-io/terratest/modules/logger"
	"github.com/stretchr/testify/assert"
	"sigs.k8s.io/kind/pkg/cluster"
)

const kindClusterName string = "kubernetes-deployment-test"
const kindConfigPath string = "../../resources/kube-config.yaml"
const kindContext string = "kind-" + kindClusterName
const kindNodeImage string = "kindest/node:v1.21.1"

func TestMain(m *testing.M) {
	t := &testing.T{}
	logger.Log(t, fmt.Sprintf("Creating kind cluster with name '%s' and image '%s'", kindClusterName, kindNodeImage))
	err := createKindCluster(kindClusterName, kindNodeImage, kindConfigPath)
	if err != nil {
		logger.Log(t, fmt.Sprintf("Failed to create kind cluster with name '%s' and image '%s'", kindClusterName, kindNodeImage))
		logger.Log(t, fmt.Sprintf("Error: %v", err))
		os.Exit(2) // Exit code 2 is used to indicate that the test setup failed
	}

	logger.Log(t, fmt.Sprintf("Kind cluster with name '%s' and image '%s' created successfully", kindClusterName, kindNodeImage))
	logger.Log(t, "Running tests...")

	exitVal := m.Run()
	logger.Log(t, fmt.Sprintf("Tests finished with exit code %d", exitVal))

	logger.Log(t, fmt.Sprintf("Deleting kind cluster with name '%s'", kindClusterName))
	err = deleteKindCluster()
	if err != nil {
		logger.Log(t, fmt.Sprintf("Failed to delete kind cluster with name '%s'", kindClusterName))
		logger.Log(t, fmt.Sprintf("Error: %v", err))
		os.Exit(3) // Exit code 3 is used to indicate that the test cleanup failed
	}
	logger.Log(t, fmt.Sprintf("Kind cluster with name '%s' deleted successfully", kindClusterName))

	os.Remove(kindConfigPath)

	os.Exit(exitVal)
}

func createKindCluster(kindClusterName string, kindNodeImage string, kindConfigPath string) error {
	provider := cluster.NewProvider()
	err := provider.Create(
		kindClusterName,
		cluster.CreateWithNodeImage(kindNodeImage),
		cluster.CreateWithKubeconfigPath(kindConfigPath),
	)
	if err != nil {
		return err
	}
	return nil
}

func deleteKindCluster() error {
	provider := cluster.NewProvider()
	err := provider.Delete(kindClusterName, kindConfigPath)
	if err != nil {
		return err
	}
	return nil
}

func buildContainerImage(t *testing.T, contextPath string, dockerfilePath string, tag string) {
	buildOptions := &docker.BuildOptions{
		Tags:         []string{tag, fmt.Sprintf("docker.io/library/%s", tag), fmt.Sprintf("localhost/%s", tag)},
		OtherOptions: []string{"-f", rootDirectory + dockerfilePath},
	}
	docker.Build(t, contextPath, buildOptions)
}

func loadPodmanImageToKindCluster(image string) error {
	command := exec.Command("kind", "load", "docker-image", "-n", kindClusterName, image)
	err := command.Run()
	if err != nil {
		fmt.Printf("Error: %v", err)
		return err
	}

	return nil
}

func TestKindClusterRunning(t *testing.T) {
	// Simple test to check if the kind cluster is running
	provider := cluster.NewProvider()
	clusters, err := provider.List()
	assert.NoError(t, err)
	assert.Contains(t, clusters, kindClusterName)
}
