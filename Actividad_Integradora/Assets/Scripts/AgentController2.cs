// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2021

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

public class RobotData
{
    public int uniqueID;
    public Vector3 position;
}

public class AgentData
{
    public List<Vector3> positions;
}

public class AgentController2 : MonoBehaviour
{
    // private string url = "https://boids.us-south.cf.appdomain.cloud/";
    string serverUrl = "http://localhost:8585";
    string getRobotsEndpoint = "/getRobots";
    string getObstaclesEndpoint = "/getObstacles";
    string getBoxesEndpoint = "/getBox";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    AgentData robotsData, obstacleData, boxesData;
    GameObject[] robots, boxes; // agents
    List<Vector3> oldPositions;
    List<Vector3> newPositions;
    // Pause the simulation while we get the update from the server
    bool hold = false;
    int step = 0;

    public GameObject robotPrefab, boxPrefab, obstaclePrefab, floor;
    [SerializeField] public int NRobots, NBoxes, width, height, maxMovements;
    public float timeToUpdate, timer, dt;

    void Start()
    {
        System.Random rand = new System.Random();
        timeToUpdate = (float)rand.NextDouble();

        robotsData = new AgentData();
        obstacleData = new AgentData();
        boxesData = new AgentData();
        oldPositions = new List<Vector3>();
        newPositions = new List<Vector3>();

        robots = new GameObject[NRobots];
        boxes = new GameObject[NBoxes];

        floor.transform.localScale = new Vector3((float)width/10, 1, (float)height/10);
        floor.transform.localPosition = new Vector3((float)width/2-0.5f, 0.5f, (float)height/2-0.5f);
        
        timer = timeToUpdate;

        for (int i = 0; i < NRobots; i++) {
            robots[i] = Instantiate(robotPrefab, Vector3.zero, Quaternion.identity);
        }
        StartCoroutine(SendConfiguration());
    }

    private void Update() 
    {
        float t = timer/timeToUpdate;
        // Smooth out the transition at start and end
        dt = t * t * ( 3f - 2f*t);

        if(timer >= timeToUpdate)
        {
            timer = 0;
            hold = true;
            StartCoroutine(UpdateSimulation());
            step++;
        }

        // int boxes_left = NBoxes;
        // for (int i = 0; i < NBoxes; i++) {
        //     if (boxes[i] == null) {
        //         boxes_left--;
        //     }
        // }

        // if (step == maxMovements) {
        //     hold = true;
        // }

        if (!hold)
        {
            for (int s = 0; s < robots.Length; s++)
            {
                Vector3 interpolated = Vector3.Lerp(oldPositions[s], newPositions[s], dt);
                robots[s].transform.localPosition = interpolated;
                
                Vector3 dir = oldPositions[s] - newPositions[s];
                robots[s].transform.rotation = Quaternion.LookRotation(dir);
            }
            // Move time from the last frame
            timer += Time.deltaTime;
        }
    }
 
    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            StartCoroutine(GetRobotsData());
            StartCoroutine(GetBoxesData());
        }
    }

    IEnumerator SendConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("NRobots", NRobots.ToString());
        form.AddField("NBoxes", NBoxes.ToString());
        form.AddField("width", width.ToString());
        form.AddField("height", height.ToString());
        form.AddField("maxMovements", maxMovements.ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Configuration upload complete!");
            Debug.Log("Getting Agents positions");
            StartCoroutine(GetRobotsData());
            StartCoroutine(GetBoxesData());
            StartCoroutine(GetObstaclesData());
        }
    }

    IEnumerator GetRobotsData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getRobotsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            robotsData = JsonUtility.FromJson<AgentData>(www.downloadHandler.text);

            // Store the old positions for each agent
            oldPositions = new List<Vector3>(newPositions);

            newPositions.Clear();

            foreach(Vector3 v in robotsData.positions)
                newPositions.Add(v);

            hold = false;
        }
    }

    IEnumerator GetBoxesData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getBoxesEndpoint);
        yield return www.SendWebRequest();

        foreach (GameObject box in boxes) {
            Destroy(box);
        }
        Debug.Log("boxes size: " + boxes.Length);
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            boxesData = JsonUtility.FromJson<AgentData>(www.downloadHandler.text);

            Debug.Log(boxesData.positions);

            for (int i = 0; i < NBoxes; i++) {
                boxes[i] = Instantiate(boxPrefab, boxesData.positions[i], Quaternion.identity);
            }
        }
    }

    IEnumerator GetObstaclesData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getObstaclesEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            obstacleData = JsonUtility.FromJson<AgentData>(www.downloadHandler.text);

            Debug.Log(obstacleData.positions);

            foreach(Vector3 position in obstacleData.positions)
            {
                Instantiate(obstaclePrefab, position, Quaternion.identity);
            }
        }
    }
}