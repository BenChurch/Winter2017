#include <array>
#include <fstream>
#include <iostream>
#include <math.h>		// For computation of nodes' sigmoidal-exponential activation function
#include <stdlib.h>		// For .txt file strings to int representations, and random number generation
#include <sstream>		// For .csv file reading
#include <string>
#include <time.h>		// Used to seed random number generator
#include <vector>
#include <Windows.h>

using namespace std;

static const char * Dir = ".";	// Using current directory
static const char * INPUT_FILE_NAME = "Input.csv";
static const char * OUTPUT_FILE_NAME = "Output.txt";

static const int MAX_COBB_ANGLE = 120;      // Maps the network's [0, 1] range output to 0 deg to MAX_COBB_ANGLE deg

static const int MAX_TRAINING_EPOCHS = 15;

static const int NUM_HIDDEN_LAYERS = 1;
static const int NUMS_HIDDEN_NODES[1] = {10};
static const double LEARNING_RATE = 0.15;
static const double MOMENTUM = 0;
static const double INITIAL_THRESHOLDS = 0.5;   // Initial threshold value for NON-INPUT nodes

class LandmarkPoint
{
public:
	string Name;
	double Position[3];
};

class LandmarksNode
{
public:
	string Name;
	double TrueCurvature;
	string InfCritVert;
	string SupCritVert;
	vector<LandmarkPoint> LandmarkPoints;
};

class LandmarkSets
{
public:
	vector<LandmarksNode> MarkupNodes;
	
	vector<LandmarksNode> TrainingData;
	vector<LandmarksNode> TestingData;

	void ReadInputData(const char * FileName);
	void PrintAllData();

	void SeperateTestAndTrainData(double TestFraction);
	void ShuffleTestingData();
	void ShuffleTrainingData();
	void PrintTestingData();
	void PrintTrainingData();

	// Each of these writes 2 .csv files, one for coords, one for angles, in a fashion suitable for MATLAB use 
	void WriteTestingData(string FileID);
	void WriteTrainingData(string FileID);
  void WriteAllData(string FileID);
};

void LandmarkSets::ReadInputData(const char * FileName)
{
	SetCurrentDirectoryA(Dir);
	ifstream InputData(FileName);
	string Line;
	if (InputData.is_open())
	{
		if (!getline(InputData, Line))
		{
			cout << "Input data file contains no recognizable data sets." << endl;
			cout << "	Data read returning empty data structure." << endl;
			InputData.close();
			return;
		}
		//cout << Line << endl;
		stringstream LineStream(Line);
		string Cell;
		getline(LineStream, Cell, ',');
		while ((Cell != "Max angle:") > 0)
		{	// Iterate through headers
			Cell.clear();
			if (!getline(InputData, Line))
			{
				cout << "Input data file contains no recognizable data sets." << endl;
				cout << "	Data read returning empty data structure." << endl;
				InputData.close();
				return;
			}
			LineStream.ignore();
			stringstream LineStream(Line);
			getline(LineStream, Cell, ',');
		}
		// ASSERT we are at the first landmark set and the input set is not empty
		LineStream.str(Line);
		getline(LineStream, Cell, ',');
		Cell.clear();
		getline(LineStream, Cell, ',');
		LandmarksNode CurrentLandmarkSet;
		CurrentLandmarkSet.TrueCurvature = atof(Cell.c_str());
		Cell.clear();
		getline(LineStream, Cell, ',');
		CurrentLandmarkSet.InfCritVert = Cell;
		Cell.clear();
		getline(LineStream, Cell, ',');
		CurrentLandmarkSet.SupCritVert = Cell;
		Cell.clear();
		getline(LineStream, Cell, ',');
		CurrentLandmarkSet.Name = Cell;

		while (getline(InputData, Line))
		{	// The structure of the rest of the document is known
			while (Cell != "Max angle:" && Cell != "EOF")
			{
				stringstream LineStream(Line);
				Cell.clear();
				getline(LineStream, Cell, ',');
				LandmarkPoint CurrentLandmarkPoint;
				CurrentLandmarkPoint.Name = Cell;
				for (int dim = 0; dim < 3; dim++)
				{
					getline(LineStream, Cell, ',');
					CurrentLandmarkPoint.Position[dim] = atof(Cell.c_str());
				}
				CurrentLandmarkSet.LandmarkPoints.push_back(CurrentLandmarkPoint);
				getline(InputData, Line);
				LineStream.ignore();
				LineStream.str(Line);
				Cell = Line.substr(0, Line.find_first_of(','));
			}
			this->MarkupNodes.push_back(CurrentLandmarkSet);
			CurrentLandmarkSet.LandmarkPoints.clear();
			if (Cell == "EOF")
			{
				InputData.close();
				return;
			}
			else
			{	// Cell == "Max angle"
				stringstream LineStream(Line);
				getline(LineStream, Cell, ',');
				Cell.clear();
				getline(LineStream, Cell, ',');
				CurrentLandmarkSet.TrueCurvature = atof(Cell.c_str());
				Cell.clear();
				getline(LineStream, Cell, ',');
				CurrentLandmarkSet.InfCritVert = Cell;
				Cell.clear();
				getline(LineStream, Cell, ',');
				CurrentLandmarkSet.SupCritVert = Cell;
				Cell.clear();
				getline(LineStream, Cell, ',');
				CurrentLandmarkSet.Name = Cell;
			}
		}
		InputData.close();
	}

}

void LandmarkSets::PrintAllData()
{
	LandmarksNode CurrentMarkupsNode;
	LandmarkPoint CurrentLandmarkPoint;
	for (int LandmarkSet = 0; LandmarkSet < this->MarkupNodes.size(); LandmarkSet++)
	{
		CurrentMarkupsNode = this->MarkupNodes[LandmarkSet];
		cout << CurrentMarkupsNode.Name << "	True curvature: " << CurrentMarkupsNode.TrueCurvature
			<< "	SupCritVert: " << CurrentMarkupsNode.SupCritVert << "	InfCritVert" << CurrentMarkupsNode.InfCritVert << endl;
		cout << "		" << "RL" << "		" << "AP" << "		" << "SI" << endl;
		for (int LandmarkPoint = 0; LandmarkPoint < CurrentMarkupsNode.LandmarkPoints.size(); LandmarkPoint++)
		{
			CurrentLandmarkPoint = CurrentMarkupsNode.LandmarkPoints[LandmarkPoint];
			cout << CurrentLandmarkPoint.Name << "	";
			for (int dim = 0; dim < 3; dim++)
			{
				cout << CurrentLandmarkPoint.Position[dim] << "	";
			}
			cout << endl;
		}
		cout << endl;
	}
}

void LandmarkSets::SeperateTestAndTrainData(double TestFraction)
{
	if (TestFraction < 0 || TestFraction > 1)
	{
		cout << "Error - invalid test fraction, cannot have fewer than none or more than all data in a set." << endl;
		cout << "	Therefore doing nothing." << endl;
		return;
	}

	int TestSetIndex;
	int TrainSetIndex;
	int TestAmount = TestFraction * this->MarkupNodes.size();
	vector<LandmarksNode> RestorationSets = (*this).MarkupNodes;	// this.MarkupsNodes will be depopulated during assignment, need to restore it after
	vector<LandmarksNode>::iterator SetIt;
	while (TestAmount > 0)
	{
		SetIt = this->MarkupNodes.begin();
		TestSetIndex = (rand() % this->MarkupNodes.size());
		SetIt += TestSetIndex;
		this->TestingData.push_back(this->MarkupNodes[TestSetIndex]);
		this->MarkupNodes.erase(SetIt);
		TestAmount--;
	}
	while (this->MarkupNodes.size() > 0)
	{	// The remaining sets go to training data
		SetIt = this->MarkupNodes.begin();
		TrainSetIndex = (rand() % this->MarkupNodes.size());
		SetIt += TrainSetIndex;
		this->TrainingData.push_back(this->MarkupNodes[TrainSetIndex]);
		this->MarkupNodes.erase(SetIt);
	}
	this->MarkupNodes = RestorationSets;
}

void LandmarkSets::ShuffleTestingData()
{
	vector<LandmarksNode> ShuffledTestData;
	vector<LandmarksNode>::iterator SetIt;
	LandmarksNode RandomLandmarkSet;
	int RandomLandmarkSetIndex;
	int OrigingalTestingDataSize = this->TestingData.size();
	for (int LandmarkSet = 0; LandmarkSet < OrigingalTestingDataSize; LandmarkSet++)
	{
		SetIt = this->TestingData.begin();
		RandomLandmarkSetIndex = (rand() % this->TestingData.size());
		SetIt += RandomLandmarkSetIndex;
		RandomLandmarkSet = this->TestingData[RandomLandmarkSetIndex];
		ShuffledTestData.push_back(RandomLandmarkSet);
		this->TestingData.erase(SetIt);
	}
	this->TestingData = ShuffledTestData;
}

void LandmarkSets::ShuffleTrainingData()
{
	vector<LandmarksNode> ShuffledTrainData;
	vector<LandmarksNode>::iterator SetIt;
	LandmarksNode RandomLandmarkSet;
	int RandomLandmarkSetIndex;
	int OrigingalTraininDataSize = this->TrainingData.size();
	for (int LandmarkSet = 0; LandmarkSet < OrigingalTraininDataSize; LandmarkSet++)
	{
		SetIt = this->TrainingData.begin();
		RandomLandmarkSetIndex = (rand() % this->TrainingData.size());
		SetIt += RandomLandmarkSetIndex;
		RandomLandmarkSet = this->TrainingData[RandomLandmarkSetIndex];
		ShuffledTrainData.push_back(RandomLandmarkSet);
		this->TrainingData.erase(SetIt);
	}
	this->TrainingData = ShuffledTrainData;
}

void LandmarkSets::PrintTestingData()
{
	LandmarksNode CurrentSetNode;
	LandmarkPoint CurrentLandmarkPoint;
	for (int TestSet = 0; TestSet < this->TestingData.size(); TestSet++)
	{
		CurrentSetNode = this->TestingData[TestSet];
		cout << CurrentSetNode.Name << " (testing set)	" << "True curvature: " << CurrentSetNode.TrueCurvature << endl;
		cout << "		" << "RL" << "		" << "AP" << "		" << "SI" << endl;
		for (int LandmarkPoint = 0; LandmarkPoint < CurrentSetNode.LandmarkPoints.size(); LandmarkPoint++)
		{
			CurrentLandmarkPoint = CurrentSetNode.LandmarkPoints[LandmarkPoint];
			cout << CurrentLandmarkPoint.Name << "	";
			for (int dim = 0; dim < 3; dim++)
			{
				cout << CurrentLandmarkPoint.Position[dim] << "	";
			}
			cout << endl;
		}
		cout << endl;
	}
}

void LandmarkSets::PrintTrainingData()
{
	LandmarksNode CurrentSetNode;
	LandmarkPoint CurrentLandmarkPoint;
	for (int TrainSet = 0; TrainSet < this->TrainingData.size(); TrainSet++)
	{
		CurrentSetNode = this->TrainingData[TrainSet];
		cout << CurrentSetNode.Name << " (training set)	" << "True curvature: " << CurrentSetNode.TrueCurvature << endl;
		cout << "		" << "RL" << "		" << "AP" << "		" << "SI" << endl;
		for (int LandmarkPoint = 0; LandmarkPoint < CurrentSetNode.LandmarkPoints.size(); LandmarkPoint++)
		{
			CurrentLandmarkPoint = CurrentSetNode.LandmarkPoints[LandmarkPoint];
			cout << CurrentLandmarkPoint.Name << "	";
			for (int dim = 0; dim < 3; dim++)
			{
				cout << CurrentLandmarkPoint.Position[dim] << "	";
			}
			cout << endl;
		}
		cout << endl;
	}
}

void LandmarkSets::WriteTestingData(string FileID)
{
	ofstream CoordsOutput, AnglesOutput;
	CoordsOutput.open("TestingCoords_" + FileID + ".txt");
	AnglesOutput.open("TestingAngles_" + FileID + ".txt");
	string line;

	LandmarksNode CurrentSetNode;
	LandmarkPoint CurrentLandmarkPoint;
	for (int TestSet = 0; TestSet < this->TestingData.size(); TestSet++)
	{
		CurrentSetNode = this->TestingData[TestSet];
		for (int LandmarkPoint = 0; LandmarkPoint < CurrentSetNode.LandmarkPoints.size(); LandmarkPoint++)
		{
			CurrentLandmarkPoint = CurrentSetNode.LandmarkPoints[LandmarkPoint];
      for (int dim = 0; dim < 3; dim++)
			  line += to_string((CurrentLandmarkPoint).Position[dim]) + ", ";
		}
    line.pop_back();  // Pops off excess " "
    line.pop_back();  // Pops off excess ","
    CoordsOutput << line << endl;
    line.clear();
    AnglesOutput << (CurrentSetNode.TrueCurvature) / 180 << endl;
	}
	CoordsOutput.close();
	AnglesOutput.close();
}

void LandmarkSets::WriteTrainingData(string FileID)
{
	ofstream CoordsOutput, AnglesOutput;
	CoordsOutput.open("TrainingCoords_" + FileID + ".txt");
	AnglesOutput.open("TrainingAngles_" + FileID + ".txt");
	string line;

	LandmarksNode CurrentSetNode;
	LandmarkPoint CurrentLandmarkPoint;
	for (int TestSet = 0; TestSet < this->TrainingData.size(); TestSet++)
	{
		CurrentSetNode = this->TrainingData[TestSet];
    for (int LandmarkPoint = 0; LandmarkPoint < CurrentSetNode.LandmarkPoints.size(); LandmarkPoint++)
    {
      CurrentLandmarkPoint = CurrentSetNode.LandmarkPoints[LandmarkPoint];
      for (int dim = 0; dim < 3; dim++)
        line += to_string((CurrentLandmarkPoint).Position[dim]) + ", ";
    }
    line.pop_back();  // Pops off excess " "
    line.pop_back();  // Pops off excess ","
    CoordsOutput << line << endl;
    line.clear();
    AnglesOutput << (CurrentSetNode.TrueCurvature) / 180 << endl;
	}
	CoordsOutput.close();
	AnglesOutput.close();
}

void LandmarkSets::WriteAllData(string FileID)
{
  ofstream CoordsOutput, TargetOutput;
  CoordsOutput.open("AllCoords_" + FileID + ".txt");
  TargetOutput.open("AllAngles_" + FileID + ".txt");
  string line;

  LandmarksNode CurrentSetNode;
  LandmarkPoint CurrentLandmarkPoint;
  for (int Set = 0; Set < this->TrainingData.size() + this->TestingData.size(); Set++)
  {
    if (Set < this->TrainingData.size())
      CurrentSetNode = this->TrainingData[Set];
    else CurrentSetNode = this->TestingData[Set - this->TrainingData.size()];
    for (int LandmarkPoint = 0; LandmarkPoint < CurrentSetNode.LandmarkPoints.size(); LandmarkPoint++)
    {
      CurrentLandmarkPoint = CurrentSetNode.LandmarkPoints[LandmarkPoint];
      for (int dim = 0; dim < 3; dim++)
        line += to_string((CurrentLandmarkPoint).Position[dim]) + ", ";
    }
    line.pop_back();  // Pops off excess " "
    line.pop_back();  // Pops off excess ","
    CoordsOutput << line << endl;
    line.clear();
    TargetOutput << ((CurrentSetNode.TrueCurvature) / MAX_COBB_ANGLE) << endl;
  }
  CoordsOutput.close();
  TargetOutput.close();
}

class Node
{
public:
	// Default constructor needs Weight and Threhsold values
	Node(vector<double> InitialWeights, double InitialThreshold);

	// Allocate/instantiate node attributes
	vector<double> Inputs;
	vector<double> Weights;
	double Threshold;
	double ActivationPotential = 0;

	void ComputeIdentityActivation();
	void ComputeSigmoidalActivation();
};

Node::Node(vector<double> InitialWeights, double InitialThreshold)
{
	for (int Weight = 0; Weight < InitialWeights.size(); Weight++)
	{
		this->Inputs.push_back(0);	// Initialize inputs while we're at it
		this->Weights.push_back(InitialWeights[Weight]);
	}
	this->Threshold = InitialThreshold;
}

void Node::ComputeIdentityActivation()
{
	// Reinitialize activation potential
	this->ActivationPotential = 0;
	for (int Input = 0; Input < this->Inputs.size(); Input++)
	{
		this->ActivationPotential += (this->Inputs[Input]) * (this->Weights[Input]);
	}
}

void Node::ComputeSigmoidalActivation()
{
	// Reinitialize activation potential
	this->ActivationPotential = 0;
	double Net = 0;
	for (int Input = 0; Input < this->Inputs.size(); Input++)
	{
		 Net += (this->Inputs[Input]) * (this->Weights[Input]);
	}
	this->ActivationPotential = 1.0 / (1 + exp((-1) * Net));
}

class FeedforwardLayeredNetwork
{
public:
	FeedforwardLayeredNetwork();

	double AngleEstimate;
	string InferiorCriticalVertebraEstimate;
	string SuperiorCriticalVertebraEstimate;
	double MSE = 0;
	vector<double> Error;	// Store error value for each output node, for each input's error

	// Catalogue of possible landmarked vertebrae to convert network critical vertebrae estimates to numbers to error
	vector<string> Vertebrae;

	vector<vector<Node>> InputLayer;     // Try organizing input analogously to spinal geometry    InputLayer[Vertebra][0] == Left     InputLayer[Vertebra][1] == Right
	vector<vector<Node>> HiddenLayers;
	vector<Node> OutputLayer;				// Contains 18 nodes, first for curvature estimation, 17 more to identify the two critical vertebrae

	double LearningRate = LEARNING_RATE;
	double Momentum = MOMENTUM;				// THIS WONT WORK EACH WEIGHT NEEDS MOMENTUM ????
	
	double ErrorOffset = 0.45;			// Used to push the weights past the minimum adjustment required for correctness

	void ConstructNetwork();

	void Feedforward(vector<LandmarkPoint> PatientLandmarks);
	void Backpropagate(double CorrectAngle);
	void BackpropagateOneLayer(double CorrectAngle, string InferiorVertebra, string SuperiorVertebra);

	void ComputeError(double CorrectAngle, string InferiorVertebra, string SuperiorVertebra);					// Updates this->MSE based on outputNode states

	void Train(LandmarkSets AllData);					// Will call Test() to gauge performance
	double Test(vector<LandmarksNode> TestData);		// Return mean-squarred-error

	void WriteSelf(string FileIdentifier);
private:

};
FeedforwardLayeredNetwork::FeedforwardLayeredNetwork()
{
	SetCurrentDirectoryA(Dir);
	srand(time(NULL));			// Provide random number seed for random weight initialization
	// Catalogue of possible landmarked vertebrae to convert network critical vertebrae estimates to numbers to error
	this->Vertebrae = { "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12", "L1", "L2", "L3", "L4", "L5" };
}

void FeedforwardLayeredNetwork::ConstructNetwork()
{
	// Currently assuming that all input points contain the same number of points
  int RandomIntLeft;
  double RandomDoubleLeft;
  int RandomIntRight;
  double RandomDoubleRight;
  vector<double> InitialInputWeightLeft;
  vector<double> InitialInputWeightRight;
  vector<Node> CurrentLeftPoint;
  vector<Node> CurrentRightPoint;
  for (int LandmarkPoint = 0; LandmarkPoint < 34; LandmarkPoint+=2) // 34 being 2 * numberOfVertebrae           
  {
	for (int dim = 0; dim < 3; dim++)
	{
		RandomIntLeft = (rand() % 100);     // Random number in the range of [0,100]
		RandomDoubleLeft = (double)(RandomIntLeft) / 100.0;
		RandomIntRight = (rand() % 100);     // Random number in the range of [0,100]
		RandomDoubleRight = (double)(RandomIntRight) / 100.0;
		CurrentLeftPoint.push_back(Node({RandomDoubleLeft}, 0));
		CurrentRightPoint.push_back(Node({ RandomDoubleRight }, 0));
	}
	this->InputLayer.push_back(CurrentLeftPoint);
	this->InputLayer.push_back(CurrentRightPoint);
	CurrentLeftPoint.clear();
	CurrentRightPoint.clear();
  }


  vector<Node> CurrentHiddenLayer;
  int RandomInt;
  double RandomDouble;
  vector<double> CurrentNodeInitialWeights;
  for (int HiddenLayer = 0; HiddenLayer < NUM_HIDDEN_LAYERS; HiddenLayer++)
  {
    for (int LayerNode = 0; LayerNode < NUMS_HIDDEN_NODES[HiddenLayer]; LayerNode++)
    {
		for (int InputNode = 0; InputNode < this->InputLayer.size() * 6; InputNode++)
		{
			RandomInt = (rand() % 100);
			RandomDouble = (double)(RandomInt) / 100.0;
			CurrentNodeInitialWeights.push_back(RandomDouble);
		}
		Node CurrentLayerNode(CurrentNodeInitialWeights, 0.5);
		CurrentNodeInitialWeights.clear();
		CurrentHiddenLayer.push_back(CurrentLayerNode);
    }
	this->HiddenLayers.push_back(CurrentHiddenLayer);
  }

  for (int OutputNode = 0; OutputNode < 18; OutputNode++)		// Magic number: 18, first node for angle estimation, 17 more to identify the critical vertebrae
  {
	  for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[this->HiddenLayers.size()-1].size(); HiddenNode++)
	  {
		  RandomInt = (rand() % 100);
		  RandomDouble = (double)(RandomInt) / 100.0;
		  CurrentNodeInitialWeights.push_back(RandomDouble);
	  }
	  Node CurrentOutputNode(CurrentNodeInitialWeights, 0.5);
	  CurrentNodeInitialWeights.clear();
	  this->OutputLayer.push_back(CurrentOutputNode);
  }

}

void FeedforwardLayeredNetwork::Feedforward(vector<LandmarkPoint> PatientLandmarks)
{
	LandmarkPoint * CurrentLandmarkPoint;

	// Reinitialize hidden node inputs (input node inputs are simply overwritten, these are summated)
	for (int HiddenLayer = 0; HiddenLayer < this->HiddenLayers.size(); HiddenLayer++)
		for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[HiddenLayer].size(); HiddenNode++)
			for (int Input = 0; Input < this->HiddenLayers[HiddenLayer][HiddenNode].Inputs.size(); Input++)
				this->HiddenLayers[HiddenLayer][HiddenNode].Inputs[Input] = 0;

	// Reinitialize output node inputs
	for (int OutputNode = 0; OutputNode < this->OutputLayer.size(); OutputNode++)
		for (int Input = 0; Input < this->OutputLayer[OutputNode].Inputs.size(); Input++)
			this->OutputLayer[OutputNode].Inputs[Input] = 0;

	for (int Landmark = 0; Landmark < PatientLandmarks.size(); Landmark++)
	{
		// We will assume that Landmarks are ordered properly, L-R-L-R-etc...
		for (int dim = 0; dim < 3; dim++)
		{
			this->InputLayer[Landmark][dim].Inputs[0] = PatientLandmarks[Landmark].Position[dim];
			this->InputLayer[Landmark][dim].ComputeIdentityActivation();
			for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[0].size(); HiddenNode++)
			{	// Seems a little odd to put this here, but makes looping through hidden layers easier
				this->HiddenLayers[0][HiddenNode].Inputs[(Landmark * 3) + dim] += this->HiddenLayers[0][HiddenNode].Weights[(Landmark * 3) + dim] * this->InputLayer[Landmark][dim].ActivationPotential;
			}
		}
	}	// ASSERT all InputNodes are at equilibrium with input

	Node * CurrentInputNode;
	Node * CurrentHiddenNode;
	for (int HiddenLayer = 0; HiddenLayer < this->HiddenLayers.size() - 1; HiddenLayer++)
	{	// Minus one to deal with the boundary condition of the output layer, as was done with odd hidden input initialization
		for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[HiddenLayer].size(); HiddenNode++)
		{	
			this->HiddenLayers[HiddenLayer][HiddenNode].ComputeSigmoidalActivation();
			for (int NextLayerNode = 0; NextLayerNode < this->HiddenLayers[HiddenLayer + 1].size(); NextLayerNode++)
			{
				this->HiddenLayers[HiddenLayer + 1][NextLayerNode].Inputs[HiddenNode] += this->HiddenLayers[HiddenLayer + 1][NextLayerNode].Weights[HiddenNode] * this->HiddenLayers[HiddenLayer][HiddenNode].ActivationPotential;
			}
		}
	}	// ASSERT all HiddenLayers Node's inputs are at equilibrium, and all HiddenLayers Node's Activations at equilibrium except last layer

	for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[this->HiddenLayers.size() - 1].size(); HiddenNode++)
	{
		this->HiddenLayers[this->HiddenLayers.size() - 1][HiddenNode].ComputeSigmoidalActivation();
		for (int OutputNode = 0; OutputNode < this->OutputLayer.size(); OutputNode++)
		{	// Should only contain one node for one angle
			this->OutputLayer[OutputNode].Inputs[HiddenNode] += this->OutputLayer[OutputNode].Weights[HiddenNode] * this->HiddenLayers[this->HiddenLayers.size() - 1][HiddenNode].ActivationPotential;
		}
	}	// ASSERT all HiddenLayers Nodes inputs and activations and OutputLayer's inputs in equilibrium

	for (int OutputNode = 0; OutputNode < this->OutputLayer.size(); OutputNode++)
	{
		this->OutputLayer[OutputNode].ComputeSigmoidalActivation();
	}	// ASSERT entire network in equilibrium
	
	// Map output in range [0, 1] to angle in range [-150deg, 150deg]
  this->AngleEstimate = (this->OutputLayer[0].ActivationPotential - 0.5) * 2 * MAX_COBB_ANGLE;

  // Identify which identification nodes are active
  Node * CurrentOutputNode;
  double LargestActivation = 0;
  int LargestActivationNode = 0;
  double SecondLargestActivation = 0;
  int SecondLargestActivationNode = 0;
  for (int OutputNode = 1; OutputNode < this->OutputLayer.size(); OutputNode++)
  {
    CurrentOutputNode = &(this->OutputLayer[OutputNode]);
    if (((*CurrentOutputNode).ActivationPotential > LargestActivation) && (*CurrentOutputNode).ActivationPotential > (*CurrentOutputNode).Threshold)
    {
      SecondLargestActivation = LargestActivation;
      SecondLargestActivationNode = LargestActivationNode;
      LargestActivation = (*CurrentOutputNode).ActivationPotential;
      LargestActivationNode = OutputNode;
    }
    else if (((*CurrentOutputNode).ActivationPotential > SecondLargestActivation) && (*CurrentOutputNode).ActivationPotential > (*CurrentOutputNode).Threshold)
    {
      SecondLargestActivation = (*CurrentOutputNode).ActivationPotential;
      SecondLargestActivationNode = OutputNode;
    }
  }
  if (SecondLargestActivationNode > LargestActivationNode)
  {
	  this->InferiorCriticalVertebraEstimate = this->Vertebrae[SecondLargestActivationNode - 1];
	  this->SuperiorCriticalVertebraEstimate = this->Vertebrae[LargestActivationNode - 1];
  }
  else
  {
	  this->InferiorCriticalVertebraEstimate = this->Vertebrae[LargestActivationNode - 1];
	  this->SuperiorCriticalVertebraEstimate = this->Vertebrae[SecondLargestActivationNode - 1];
  }
  
}

void FeedforwardLayeredNetwork::Backpropagate(double CorrectAngle)
{
	double SumSquaredError = 0;
	double LastWeightChange = 0;			// Used with momentum feature
	double Output;

	Node * CurrentOutputNode;
	Node * CurrentHiddenNode;
	Node * FeedingNode;						// Points to node who feeds input corresponding to weight being changed
	double NewDelta;

	vector<double> ErrorVector;				// Stores output nodes errors, and used to calculate deltas
	vector<vector<double>> HiddenDeltas;	// Stores weight change factors computed from gradient descent
	vector<double> HiddenDeltaLayer;		// Stores each hidden layers deltas to push onto HiddenDeltas

	for (int OutputNode = 0; OutputNode < this->OutputLayer.size(); OutputNode++)
	{	
		CurrentOutputNode = &(this->OutputLayer[OutputNode]);
		Output = ((*CurrentOutputNode).ActivationPotential - 0.5) * 360;	// Subtract 0.5 and multiply by 180 to map [0,1] to [-180,180]
		SumSquaredError += (CorrectAngle - Output) * (CorrectAngle - Output);
		ErrorVector.push_back(CorrectAngle - Output);
		HiddenDeltaLayer.push_back(ErrorVector[OutputNode] * (*CurrentOutputNode).ActivationPotential * (1 - (*CurrentOutputNode).ActivationPotential));
		for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[this->HiddenLayers.size() - 1].size(); HiddenNode++)
		{
			(*CurrentOutputNode).Weights[HiddenNode] += (this->LearningRate) * ((*CurrentOutputNode).Inputs[HiddenNode]) * (HiddenDeltaLayer[OutputNode])
				+ (this->Momentum * LastWeightChange);
			LastWeightChange = (this->LearningRate) * ((*CurrentOutputNode).Inputs[HiddenNode]) * (HiddenDeltaLayer[OutputNode])
				+ (this->Momentum * LastWeightChange);
		}
	}	// ASSERT that all output nodes' weights have been adjusted

	HiddenDeltas.push_back(HiddenDeltaLayer);
	HiddenDeltaLayer.clear();
	for (int HiddenLayer = this->HiddenLayers.size() - 1; HiddenLayer >= 1; HiddenLayer--)
	{
		for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[HiddenLayer].size(); HiddenNode++)
		{
			NewDelta = 0;
			CurrentHiddenNode = &(this->HiddenLayers[HiddenLayer][HiddenNode]);
			for (int RemainingHiddenLayer = this->HiddenLayers.size() - HiddenLayer - 1; RemainingHiddenLayer >= 0; RemainingHiddenLayer--)
			{
				for (int RemainingLayerNode = 0; RemainingLayerNode < this->HiddenLayers[RemainingHiddenLayer].size(); RemainingLayerNode++)
				{
					NewDelta += HiddenDeltas[RemainingHiddenLayer][RemainingLayerNode] * (this->HiddenLayers[RemainingHiddenLayer][RemainingLayerNode].Weights[HiddenNode]);
				}
			}
			HiddenDeltaLayer.push_back(NewDelta * (*CurrentHiddenNode).ActivationPotential * (1 - (*CurrentHiddenNode).ActivationPotential));
		}
		HiddenDeltas.push_back(HiddenDeltaLayer);
		HiddenDeltaLayer.clear();
		for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[HiddenLayer].size(); HiddenNode++)
		{
			CurrentHiddenNode = &(this->HiddenLayers[HiddenLayer][HiddenNode]);
			for (int HiddenNodeWeight = 0; HiddenNodeWeight < (*CurrentHiddenNode).Weights.size(); HiddenNodeWeight++)
			{
				FeedingNode = &(this->HiddenLayers[HiddenLayer - 1][HiddenNodeWeight]);
				(*CurrentHiddenNode).Weights[HiddenNodeWeight] += (this->LearningRate) * (HiddenDeltas[this->HiddenLayers.size() - HiddenLayer - 1][HiddenNode])* ((*FeedingNode).ActivationPotential);
			}
		}
	}	// ASSERT that all weights have been updated except those connecting input to first layer of hidden nodes

	for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[0].size(); HiddenNode++)
	{
		NewDelta = 0;
		CurrentHiddenNode = &(this->HiddenLayers[0][HiddenNode]);
		for (int RemainingHiddenLayer = this->HiddenLayers.size() - 1; RemainingHiddenLayer >= 0; RemainingHiddenLayer--)
		{
			for (int RemainingLayerNode = this->HiddenLayers.size() - 1; RemainingLayerNode > 0; RemainingLayerNode--)
			{
				NewDelta += HiddenDeltas[RemainingHiddenLayer][RemainingLayerNode] * (this->HiddenLayers[RemainingHiddenLayer][RemainingLayerNode].Weights[HiddenNode]);		// CANT BE RIGHT, HiddenNode not connected to HiddenLayerss[][]
			}
		}
		HiddenDeltaLayer.push_back(NewDelta * (*CurrentHiddenNode).ActivationPotential * (1 - (*CurrentHiddenNode).ActivationPotential));
	}
	HiddenDeltas.push_back(HiddenDeltaLayer);
	HiddenDeltaLayer.clear();

	for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[0].size(); HiddenNode++)
	{
		CurrentHiddenNode = &(this->HiddenLayers[0][HiddenNode]);
		for (int HiddenNodeWeight = 0; HiddenNodeWeight < (*CurrentHiddenNode).Weights.size(); HiddenNodeWeight++)
		{
			FeedingNode = &(this->InputLayer[HiddenNodeWeight / 3][HiddenNodeWeight % 3]);
			(*CurrentHiddenNode).Weights[HiddenNodeWeight] += (this->LearningRate) * (HiddenDeltas[HiddenDeltas.size() - 1][HiddenNode])* ((*FeedingNode).ActivationPotential);
		}
	}	// ASSERT that all weights have been updated
}

void FeedforwardLayeredNetwork::BackpropagateOneLayer(double CorrectAngle, string InferiorVertebra, string SuperiorVertebra)
{
	this->Error.clear();
	double LastWeightChange = 0;		      	// Used with momentum feature
	double Output;

	Node * CurrentOutputNode;
	Node * CurrentHiddenNode;
	Node * CurrentInputNode;

	vector<double> deltaHiddenToOutput;		// Stores deltas for weight changes from hidden to output layer
	vector<double> deltaInputToHidden;		
	
	this->ComputeError(CorrectAngle, InferiorVertebra, SuperiorVertebra);

	for (int OutputNode = 0; OutputNode < this->OutputLayer.size(); OutputNode++)
	{ // Now that we have ErrorVector for output state, populate Hidden
		CurrentOutputNode = &(this->OutputLayer[OutputNode]);
		deltaHiddenToOutput.push_back(this->Error[OutputNode] * ((*CurrentOutputNode).ActivationPotential) * (1 - (*CurrentOutputNode).ActivationPotential));
		for (int HiddenToOuptut = 0; HiddenToOuptut < (*CurrentOutputNode).Inputs.size(); HiddenToOuptut++)
		{
			(*CurrentOutputNode).Weights[HiddenToOuptut] += this->LearningRate * ((*CurrentOutputNode).Inputs[HiddenToOuptut]) * (deltaHiddenToOutput[OutputNode])
				+ this->Momentum * LastWeightChange;
			LastWeightChange = this->LearningRate * ((*CurrentOutputNode).Inputs[HiddenToOuptut]) * (deltaHiddenToOutput[OutputNode])
				+ this->Momentum * LastWeightChange;
		}
	}	// ASSERT OutputLayer weights are updated

	double NewDelta;
	for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[0].size(); HiddenNode++)
	{	// We are assuming we have one hidden layer
		CurrentHiddenNode = &(this->HiddenLayers[0][HiddenNode]);
		NewDelta = 0;
		for (int OutputNode = 0; OutputNode < this->OutputLayer.size(); OutputNode++)
		{
			CurrentOutputNode = &(this->OutputLayer[OutputNode]);
			NewDelta += (deltaHiddenToOutput[OutputNode]) * (*CurrentOutputNode).Weights[HiddenNode];
		}
		NewDelta = NewDelta * (*CurrentHiddenNode).ActivationPotential * (1 - (*CurrentHiddenNode).ActivationPotential);
		for (int VertebraInput = 0; VertebraInput < this->InputLayer.size(); VertebraInput++)
		{
			for (int DimensionInput = 0; DimensionInput < this->InputLayer[VertebraInput].size(); DimensionInput++)
			{
				CurrentInputNode = &(this->InputLayer[VertebraInput][DimensionInput]);
				(*CurrentHiddenNode).Weights[VertebraInput * this->InputLayer[0].size() + DimensionInput] += this->LearningRate * NewDelta * (*CurrentInputNode).ActivationPotential;
			}
			
		}
	}
}

void FeedforwardLayeredNetwork::ComputeError(double CorrectAngle, string InferiorVertebra, string SuperiorVertebra)
{
	Node * CurrentOutputNode;
	Node * CurrentHiddenNode;
	Node * CurrentInputNode;

	double AngleError;                      // First component of combined error
	double InferiorIdentificationError = 0; // Second component
	double SuperiorIdentificationError = 0; // Third
	double SumSquaredAngleError = 0;             // As suggested above
	double SumSquaredIndentificationError = 0;

	AngleError = (CorrectAngle - this->AngleEstimate);	// Angle error in degrees
	SumSquaredAngleError += AngleError * AngleError;
	this->Error.push_back(AngleError / (2*MAX_COBB_ANGLE));	// Normalize error over range [-1,1]

	int Vertebra = 0;

	while (this->Vertebrae[Vertebra] != SuperiorVertebra && this->Vertebrae[Vertebra] != this->SuperiorCriticalVertebraEstimate)
	{	// Compute vertebra identification error
		CurrentOutputNode = &(this->OutputLayer[Vertebra + 1]);
		if ((*CurrentOutputNode).ActivationPotential > (*CurrentOutputNode).Threshold - this->ErrorOffset)
		{	// If an output node was above threshold, despite not winning
			SuperiorIdentificationError = -((*CurrentOutputNode).ActivationPotential - ((*CurrentOutputNode).Threshold - this->ErrorOffset));
			this->Error.push_back(SuperiorIdentificationError);
			SumSquaredIndentificationError += SuperiorIdentificationError * SuperiorIdentificationError;
		}
		else
			this->Error.push_back(0);
		Vertebra++;
		// We haven't encountered an active node yet, or we'd be at this->SuperiorCriticalVertebraEstimate
	}
	CurrentOutputNode = &(this->OutputLayer[Vertebra + 1]);
	if (this->Vertebrae[Vertebra] == SuperiorVertebra && this->Vertebrae[Vertebra] == this->SuperiorCriticalVertebraEstimate)
	{	// We're finished with the loop, if both looping conditions were negated simultaneously, no error, wind up here
		this->Error.push_back(0);
	}
	else if (this->Vertebrae[Vertebra] == SuperiorVertebra)
	{	// We're at the vertebra that should be active, but it isn't
		SuperiorIdentificationError = ((*CurrentOutputNode).Threshold + this->ErrorOffset) - (*CurrentOutputNode).ActivationPotential;
		this->Error.push_back(SuperiorIdentificationError);
		SumSquaredIndentificationError += SuperiorIdentificationError * SuperiorIdentificationError;
	}
	else if (this->Vertebrae[Vertebra] == this->SuperiorCriticalVertebraEstimate)
	{	// We're at the node our network thinks corresponds to the critical superior vertebra, but it's wrong
		SuperiorIdentificationError = (((*CurrentOutputNode).Threshold) - ((*CurrentOutputNode).ActivationPotential + this->ErrorOffset));
		this->Error.push_back(SuperiorIdentificationError);
		SumSquaredIndentificationError += SuperiorIdentificationError * SuperiorIdentificationError;
	}
	Vertebra++;

	// Now find the inferior vertebra estimate
	while (this->Vertebrae[Vertebra] != InferiorVertebra && this->Vertebrae[Vertebra] != this->InferiorCriticalVertebraEstimate)
	{	// Compute vertebra identification error
		CurrentOutputNode = &(this->OutputLayer[Vertebra + 1]);
		if ((*CurrentOutputNode).ActivationPotential > (*CurrentOutputNode).Threshold - this->ErrorOffset)
		{	// If an output node was above threshold, despite not winning -  ***************** catches mistaken SuperiorEstimate?
			InferiorIdentificationError = (*CurrentOutputNode).Threshold - this->ErrorOffset - (*CurrentOutputNode).ActivationPotential;
			this->Error.push_back(InferiorIdentificationError);
			SumSquaredIndentificationError += InferiorIdentificationError * InferiorIdentificationError;
		}
		else if (((*CurrentOutputNode).ActivationPotential < (*CurrentOutputNode).Threshold + this->ErrorOffset) && (this->Vertebrae[Vertebra] == SuperiorVertebra))
		{	// Catches mistakes when SupCritVertEstimate is too superior - we're at the node that should have been active
			SuperiorIdentificationError = -((*CurrentOutputNode).Threshold + this->ErrorOffset) - (*CurrentOutputNode).ActivationPotential;
			this->Error.push_back(SuperiorIdentificationError);
			SumSquaredIndentificationError += SuperiorIdentificationError * SuperiorIdentificationError;
		}
		else
			this->Error.push_back(0);
		Vertebra++;
		// We haven't encountered an active node yet, or we'd be at this->InferiorCriticalVertebraEstimate
	}
	CurrentOutputNode = &(this->OutputLayer[Vertebra + 1]);
	if (this->Vertebrae[Vertebra] == InferiorVertebra && this->Vertebrae[Vertebra] == this->InferiorCriticalVertebraEstimate)
	{	// We're finished with the loop, if both looping conditions were negated simultaneously, no error, wind up here
		this->Error.push_back(0);
	}
	else if (this->Vertebrae[Vertebra] == InferiorVertebra)
	{	// We're at the vertebra that should be active, but it isn't
		InferiorIdentificationError = ((*CurrentOutputNode).Threshold + this->ErrorOffset) - (*CurrentOutputNode).ActivationPotential;
		this->Error.push_back(InferiorIdentificationError);
		SumSquaredIndentificationError += InferiorIdentificationError * InferiorIdentificationError;
	}
	else if (this->Vertebrae[Vertebra] == this->InferiorCriticalVertebraEstimate)
	{	// We're at the node our network thinks corresponds to the critical inferior vertebra, but it's wrong
		InferiorIdentificationError = (((*CurrentOutputNode).Threshold) - ((*CurrentOutputNode).ActivationPotential + this->ErrorOffset));
		this->Error.push_back(InferiorIdentificationError);
		SumSquaredIndentificationError += InferiorIdentificationError * InferiorIdentificationError;
	}

	while (this->Vertebrae[Vertebra] != "L5")
	{	// If there are still output nodes for which to calculate error
		Vertebra++;
		CurrentOutputNode = &(this->OutputLayer[Vertebra + 1]);
		if (((*CurrentOutputNode).ActivationPotential < (*CurrentOutputNode).ActivationPotential) && (this->Vertebrae[Vertebra] == InferiorVertebra))
		{	// We got to out estimate before the correct one, this catches the error on the correct one
			InferiorIdentificationError = -(((*CurrentOutputNode).Threshold + this->ErrorOffset) - (*CurrentOutputNode).ActivationPotential);
			this->Error.push_back(InferiorIdentificationError);
			SumSquaredIndentificationError += InferiorIdentificationError * InferiorIdentificationError;
			continue;
		}
		if (((*CurrentOutputNode).ActivationPotential) > ((*CurrentOutputNode).Threshold - this->ErrorOffset) && !(this->SuperiorCriticalVertebraEstimate == SuperiorVertebra || this->InferiorCriticalVertebraEstimate == InferiorVertebra))
		{	// A node is more active that should be
			SuperiorIdentificationError = ((*CurrentOutputNode).Threshold) - ((*CurrentOutputNode).ActivationPotential + this->ErrorOffset);	// Just use this to hold error
			this->Error.push_back(SuperiorIdentificationError);
			SumSquaredIndentificationError += SuperiorIdentificationError * SuperiorIdentificationError;
			continue;
		}
		if (((*CurrentOutputNode).ActivationPotential < (*CurrentOutputNode).Threshold + this->ErrorOffset) && !((this->SuperiorCriticalVertebraEstimate == SuperiorVertebra || this->InferiorCriticalVertebraEstimate == InferiorVertebra)))
		{	// If a node is less active than it should be
			InferiorIdentificationError = -(((*CurrentOutputNode).Threshold + this->ErrorOffset) - (*CurrentOutputNode).ActivationPotential);
			this->Error.push_back(InferiorIdentificationError);
			SumSquaredIndentificationError += InferiorIdentificationError * InferiorIdentificationError;
			continue;
		}
		// Make it this far, no error on this node
		this->Error.push_back(0);
	}
}

void FeedforwardLayeredNetwork::Train(LandmarkSets AllData)
{
	LandmarksNode * CurrentLandmarksNode;
	int CurrentTrainingEpoch = 0;
	double MSAngleE;
	double MSIdentE;
	while (CurrentTrainingEpoch < MAX_TRAINING_EPOCHS)
	{
		MSAngleE = 0;
		MSIdentE = 0;
		for (int LandmarkSet = 0; LandmarkSet < AllData.TrainingData.size(); LandmarkSet++)
		{
			CurrentLandmarksNode = &(AllData.TrainingData[LandmarkSet]);
			this->Feedforward((*CurrentLandmarksNode).LandmarkPoints);
			this->BackpropagateOneLayer((*CurrentLandmarksNode).TrueCurvature, (*CurrentLandmarksNode).InfCritVert, (*CurrentLandmarksNode).SupCritVert);
			cout << (*CurrentLandmarksNode).Name << endl << "	True curvature: " << (*CurrentLandmarksNode).TrueCurvature << "	Estimated curvature: " << this->AngleEstimate << endl;
			cout << "	SupCritVert: " << (*CurrentLandmarksNode).SupCritVert << "		Estimated SCV: " << this->SuperiorCriticalVertebraEstimate << endl;
			cout << "	InfCritVert: " << (*CurrentLandmarksNode).InfCritVert << "		Estimated ICV: " << this->InferiorCriticalVertebraEstimate << endl << endl;
			MSAngleE += this->Error[0] * this->Error[0];
			for (int OutputNode = 1; OutputNode < this->OutputLayer.size(); OutputNode++)
				MSIdentE += this->Error[OutputNode] * this->Error[OutputNode];

		}
		cout << "MSE (angle, deg) after epoch #" << CurrentTrainingEpoch + 1 << "	-	" << this->MSE << endl;
		CurrentTrainingEpoch++;
	}
}

double FeedforwardLayeredNetwork::Test(vector<LandmarksNode> TestData)
{
	this->MSE = 0;
	for (int LandmarkSet = 0; LandmarkSet < TestData.size(); LandmarkSet++)
	{
		this->Feedforward(TestData[LandmarkSet].LandmarkPoints);
		this->ComputeError(TestData[LandmarkSet].TrueCurvature, TestData[LandmarkSet].InfCritVert, TestData[LandmarkSet].SupCritVert);
		this->MSE += this->Error[0] * this->Error[0];	// Just use angle error, quantitative
	}
	this->MSE = this->MSE / (double(TestData.size()));
	return this->MSE;
}

void FeedforwardLayeredNetwork::WriteSelf(string FileIdentifier)						// Just used for my debugging purposes. Output doesn't necessarily line up - can be confusing
{
	ofstream SelfOutput;
	SelfOutput.open("NetworkState" + FileIdentifier + ".txt");

	vector<string> Dims = { "RL", "AP", "SI" };
	vector<string> Vertebrae = { "T1L", "T1R", "T2L", "T2R", "T3L", "T3R", "T4L", "T4R", "T5L", "T5R", "T6L", "T6R", "T7L", "T7R", "T8L", "T8R", "T9L", "T9R",
		"T10L", "T10R", "T11L", "T11R", "T12L", "T12R", "L1L", "L1R", "L2L", "L2R", "L3L", "L3R", "L4L", "L4R", "L5L", "L5R" };

	vector<Node> * CurrentNodeTrio;
	Node * CurrentNode;

	SelfOutput << "Input layer(s):" << endl;

	// Write input array
	SelfOutput << endl << "Vertebra:" << endl << "	";
	for (int Vertebra = 0; Vertebra < Vertebrae.size(); Vertebra += 2)
	{
		SelfOutput << "		" << Vertebrae[Vertebra] << "		";
	}

	SelfOutput << endl;
	SelfOutput << "InputL:		";
	for (int LeftInputPoint = 0; LeftInputPoint < this->InputLayer.size(); LeftInputPoint+=2)
	{	// Inputs
		(CurrentNodeTrio) = &(this->InputLayer[LeftInputPoint]);
		
		for (int InputNode = 0; InputNode < (*CurrentNodeTrio).size(); InputNode++)
		{	
			(CurrentNode) = &(*CurrentNodeTrio)[InputNode];
			SelfOutput << (*CurrentNode).Inputs[0] << "	";		// Input nodes having always 1 input
		}
		SelfOutput << "	";
	}

	SelfOutput << endl;
	SelfOutput << "WeightL:	";
	for (int LeftInputPoint = 0; LeftInputPoint < this->InputLayer.size(); LeftInputPoint += 2)
	{	// Weights
		(CurrentNodeTrio) = &(this->InputLayer[LeftInputPoint]);
		for (int InputNode = 0; InputNode < (*CurrentNodeTrio).size(); InputNode++)
		{
			(CurrentNode) = &(*CurrentNodeTrio)[InputNode];
			SelfOutput << (*CurrentNode).Weights[0] << "	";		// Input nodes having always 1 input
		}
		SelfOutput << "	";
	}

	SelfOutput << endl;
	SelfOutput << "ThresholdL:	";
	for (int LeftInputPoint = 0; LeftInputPoint < this->InputLayer.size(); LeftInputPoint += 2)
	{	// Threshold
		(CurrentNodeTrio) = &(this->InputLayer[LeftInputPoint]);
		for (int InputNode = 0; InputNode < (*CurrentNodeTrio).size(); InputNode++)
		{
			(CurrentNode) = &(*CurrentNodeTrio)[InputNode];
			SelfOutput << (*CurrentNode).Threshold << "	";		// Input nodes having always 1 input
		}
		SelfOutput << "	";
	}

	SelfOutput << endl;
	SelfOutput << "ActivationL:	";
	for (int LeftInputPoint = 0; LeftInputPoint < this->InputLayer.size(); LeftInputPoint += 2)
	{	// Activation
		(CurrentNodeTrio) = &(this->InputLayer[LeftInputPoint]);
		for (int InputNode = 0; InputNode < (*CurrentNodeTrio).size(); InputNode++)
		{
			(CurrentNode) = &(*CurrentNodeTrio)[InputNode];
			SelfOutput << (*CurrentNode).ActivationPotential << "	";		// Input nodes having always 1 input
		}
		SelfOutput << "	";
	}

	SelfOutput << endl << endl;
	SelfOutput << "InputR:		";
	for (int RightInputPoint = 1; RightInputPoint < this->InputLayer.size(); RightInputPoint += 2)
	{	// Inputs
		(CurrentNodeTrio) = &(this->InputLayer[RightInputPoint]);
		for (int InputNode = 0; InputNode < (*CurrentNodeTrio).size(); InputNode++)
		{
			(CurrentNode) = &(*CurrentNodeTrio)[InputNode];
			SelfOutput << (*CurrentNode).Inputs[0] << "	";		// Input nodes having always 1 input
		}
		SelfOutput << "	";
	}

	SelfOutput << endl;
	SelfOutput << "WeightR:	";
	for (int RightInputPoint = 0; RightInputPoint < this->InputLayer.size(); RightInputPoint += 2)
	{	// Weights
		(CurrentNodeTrio) = &(this->InputLayer[RightInputPoint]);
		for (int InputNode = 0; InputNode < (*CurrentNodeTrio).size(); InputNode++)
		{
			(CurrentNode) = &(*CurrentNodeTrio)[InputNode];
			SelfOutput << (*CurrentNode).Weights[0] << "	";		// Input nodes having always 1 input
		}
		SelfOutput << "	";
	}

	SelfOutput << endl;
	SelfOutput << "ThresholdR:	";
	for (int RightInputPoint = 0; RightInputPoint < this->InputLayer.size(); RightInputPoint += 2)
	{	// Threshold
		(CurrentNodeTrio) = &(this->InputLayer[RightInputPoint]);
		for (int InputNode = 0; InputNode < (*CurrentNodeTrio).size(); InputNode++)
		{
			(CurrentNode) = &(*CurrentNodeTrio)[InputNode];
			SelfOutput << (*CurrentNode).Threshold << "	";		// Input nodes having always 1 input
		}
		SelfOutput << "	";
	}

	SelfOutput << endl;
	SelfOutput << "ActivationR:	";
	for (int RightInputPoint = 0; RightInputPoint < this->InputLayer.size(); RightInputPoint += 2)
	{	// Activation
		(CurrentNodeTrio) = &(this->InputLayer[RightInputPoint]);
		for (int InputNode = 0; InputNode < (*CurrentNodeTrio).size(); InputNode++)
		{
			(CurrentNode) = &(*CurrentNodeTrio)[InputNode];
			SelfOutput << (*CurrentNode).ActivationPotential << "	";		// Input nodes having always 1 input
		}
		SelfOutput << "	";
	}

	SelfOutput << endl;

	// Write hidden layer
	SelfOutput << endl << "Hidden layer(s): " << endl;
	SelfOutput << endl;
	
	for (int HiddenLayer = 0; HiddenLayer < this->HiddenLayers.size(); HiddenLayer++)
	{
		SelfOutput << "Hidden layer #" << HiddenLayer << endl;
		SelfOutput << "Inputs:	" << endl;
		for (int InputNode = 0; InputNode < this->InputLayer.size() * this->InputLayer[0].size(); InputNode++)
		{	// Inputs:
			SelfOutput << InputNode << "		";
			for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[HiddenLayer].size(); HiddenNode++)
			{
				(CurrentNode) = &(this->HiddenLayers[HiddenLayer][HiddenNode]);
				SelfOutput << (*CurrentNode).Inputs[InputNode] << "	";
			}
			SelfOutput << endl;
		}

		SelfOutput << endl;
		SelfOutput << "Weights:	" << endl;
		for (int InputNode = 0; InputNode < this->InputLayer.size() * this->InputLayer[0].size(); InputNode++)
		{	// Weights:
			SelfOutput << InputNode << "		";
			for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[HiddenLayer].size(); HiddenNode++)
			{
				(CurrentNode) = &(this->HiddenLayers[HiddenLayer][HiddenNode]);
				SelfOutput << (*CurrentNode).Weights[InputNode] << "	";
			}
			SelfOutput << endl;
		}
		SelfOutput << endl;
		SelfOutput << "Threshold:	";

		for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[HiddenLayer].size(); HiddenNode++)
		{
			(CurrentNode) = &(this->HiddenLayers[HiddenLayer][HiddenNode]);
			SelfOutput << (*CurrentNode).Threshold << "	";
		}

		SelfOutput << endl;
		SelfOutput << "Activation:	";
		for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[HiddenLayer].size(); HiddenNode++)
		{
			(CurrentNode) = &(this->HiddenLayers[HiddenLayer][HiddenNode]);
			SelfOutput << (*CurrentNode).ActivationPotential << "	";
		}
	}
	

	// Write output layer
	SelfOutput << endl;
	SelfOutput << endl << "Output layer: " << endl;
	SelfOutput << endl;

	SelfOutput << "Inputs:	" << endl;
	for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[this->HiddenLayers.size()-1].size(); HiddenNode++)
	{	// Inputs:
		SelfOutput << HiddenNode << "		";
		SelfOutput << this->OutputLayer[0].Inputs[HiddenNode] << endl;		// Hack it to OutputLayer[0] for now, only the one output angle
	}

	SelfOutput << endl;
	SelfOutput << "Weights:	" << endl;
	for (int HiddenNode = 0; HiddenNode < this->HiddenLayers[this->HiddenLayers.size()-1].size(); HiddenNode++)
	{	// Weights:
		SelfOutput << HiddenNode << "		";
		SelfOutput << this->OutputLayer[0].Weights[HiddenNode] << endl;		// Hack it to OutputLayer[0] for now, only the one output angle
	}
	SelfOutput << endl;
	SelfOutput << "Threshold:	" << this->OutputLayer[0].Threshold;

	SelfOutput << endl;
	SelfOutput << "Activation:	" << this->OutputLayer[0].ActivationPotential;
	SelfOutput << endl;

	SelfOutput.close();
}

int main()
{
	LandmarkSets InputLandmarkSets;
	InputLandmarkSets.ReadInputData(INPUT_FILE_NAME);

	 InputLandmarkSets.SeperateTestAndTrainData(0.2);  // Needed for now to get WriteAllData to work
	for (int i = 0; i < 0; i++)
	{	// Use a for-loop to write data to MATLAB csv files - DANGEROUS - make sure terminates - includes user input continuation
		cout << "Press enter to generate file set " << i+1 << " or press crtl + c to terminate program." << endl;
		cin.ignore();
		InputLandmarkSets.WriteAllData(to_string(i));
	}

	FeedforwardLayeredNetwork AngleEstimator;
	AngleEstimator.ConstructNetwork();
	AngleEstimator.WriteSelf("1");
	AngleEstimator.Train(InputLandmarkSets);

	cout << "Press enter to end the program." << endl;
	cin.ignore();
	return 0;
}

