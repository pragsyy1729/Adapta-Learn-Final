import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navigation from "@/components/Navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  ArrowLeft, 
  Clock, 
  AlertTriangle,
  CheckCircle2,
  XCircle
} from "lucide-react";

const QuizInterface = () => {
  const { quizId } = useParams();
  const navigate = useNavigate();
  
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<{ [key: number]: number }>({});
  const [timeLeft, setTimeLeft] = useState(600); // 10 minutes in seconds
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [showResults, setShowResults] = useState(false);

  // Mock quiz data
  const quiz = {
    id: quizId,
    title: "useState Mastery Quiz",
    description: "Test your understanding of React's useState hook",
    totalQuestions: 5,
    timeLimit: 600, // 10 minutes
    passScore: 70
  };

  const questions = [
    {
      id: 1,
      question: "What is the correct way to initialize state with a default value in React using useState?",
      options: [
        "const [count] = useState(0);",
        "const [count, setCount] = useState(0);",
        "const count = useState(0);",
        "const setCount = useState(0);"
      ],
      correctAnswer: 1,
      explanation: "useState returns an array with two elements: the current state value and a setter function."
    },
    {
      id: 2,
      question: "When should you use functional updates with useState?",
      options: [
        "Never, they are deprecated",
        "When the new state depends on the previous state",
        "Only with primitive values",
        "When you want to reset state to initial value"
      ],
      correctAnswer: 1,
      explanation: "Functional updates ensure you get the most current state value, especially important in concurrent updates."
    },
    {
      id: 3,
      question: "What happens when you call setState with the same value as the current state?",
      options: [
        "React always re-renders the component",
        "React throws an error",
        "React may skip the re-render (bailout)",
        "The component unmounts and remounts"
      ],
      correctAnswer: 2,
      explanation: "React uses Object.is() to compare values and may skip re-rendering if the value hasn't changed."
    },
    {
      id: 4,
      question: "How do you update an object in state correctly?",
      options: [
        "setState(prevState => { prevState.name = 'new'; return prevState; })",
        "setState(prevState => ({ ...prevState, name: 'new' }))",
        "setState({ name: 'new' })",
        "setState(prevState.name = 'new')"
      ],
      correctAnswer: 1,
      explanation: "You should create a new object to trigger a re-render, as React compares references."
    },
    {
      id: 5,
      question: "What is the initial value parameter in useState?",
      options: [
        "A value that gets called on every render",
        "A value used only during the initial render",
        "A function that returns the default state",
        "Both B and C are correct"
      ],
      correctAnswer: 3,
      explanation: "The initial value can be a value (used only once) or a function (for expensive computations)."
    }
  ];

  // Timer effect
  useEffect(() => {
    if (timeLeft > 0 && !isSubmitted) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && !isSubmitted) {
      handleSubmit();
    }
  }, [timeLeft, isSubmitted]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerSelect = (answerIndex: number) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [currentQuestion]: answerIndex
    }));
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = () => {
    setIsSubmitted(true);
    setShowResults(true);
  };

  const calculateScore = () => {
    let correct = 0;
    questions.forEach((question, index) => {
      if (selectedAnswers[index] === question.correctAnswer) {
        correct++;
      }
    });
    return Math.round((correct / questions.length) * 100);
  };

  const getAnswerStatus = (questionIndex: number, answerIndex: number) => {
    if (!showResults) return "";
    
    const question = questions[questionIndex];
    const selectedAnswer = selectedAnswers[questionIndex];
    
    if (answerIndex === question.correctAnswer) {
      return "correct";
    } else if (answerIndex === selectedAnswer && answerIndex !== question.correctAnswer) {
      return "incorrect";
    }
    return "";
  };

  if (showResults) {
    const score = calculateScore();
    const passed = score >= quiz.passScore;
    
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        
        <main className="container mx-auto px-4 py-8 pt-24">
          <Card className="max-w-4xl mx-auto">
            <CardHeader className="text-center">
              <div className="mb-4">
                {passed ? (
                  <CheckCircle2 className="w-16 h-16 text-learning-success mx-auto" />
                ) : (
                  <XCircle className="w-16 h-16 text-destructive mx-auto" />
                )}
              </div>
              <CardTitle className="text-3xl mb-2">
                Quiz {passed ? "Completed!" : "Not Passed"}
              </CardTitle>
              <p className="text-muted-foreground">
                Your score: <span className="font-bold text-2xl">{score}%</span>
              </p>
              <Badge variant={passed ? "default" : "destructive"} className="mt-2">
                {passed ? "Passed" : `Need ${quiz.passScore}% to pass`}
              </Badge>
            </CardHeader>
            
            <CardContent className="space-y-6">
              {questions.map((question, index) => (
                <div key={question.id} className="border rounded-lg p-4">
                  <h3 className="font-medium mb-3">
                    Question {index + 1}: {question.question}
                  </h3>
                  
                  <div className="space-y-2 mb-3">
                    {question.options.map((option, optionIndex) => {
                      const status = getAnswerStatus(index, optionIndex);
                      return (
                        <div 
                          key={optionIndex}
                          className={`p-2 rounded border ${
                            status === "correct" 
                              ? "bg-learning-success/20 border-learning-success" 
                              : status === "incorrect"
                                ? "bg-destructive/20 border-destructive"
                                : "bg-muted/50"
                          }`}
                        >
                          <div className="flex items-center space-x-2">
                            {status === "correct" && <CheckCircle2 className="w-4 h-4 text-learning-success" />}
                            {status === "incorrect" && <XCircle className="w-4 h-4 text-destructive" />}
                            <span>{option}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  
                  <div className="bg-gradient-card p-3 rounded border">
                    <p className="text-sm"><strong>Explanation:</strong> {question.explanation}</p>
                  </div>
                </div>
              ))}
              
              <div className="flex justify-center space-x-4">
                <Button variant="outline" onClick={() => navigate(-1)}>
                  Back to Chapter
                </Button>
                {!passed && (
                  <Button onClick={() => window.location.reload()}>
                    Retake Quiz
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  const currentQ = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 py-8 pt-24">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <Button 
              variant="ghost" 
              onClick={() => navigate(-1)}
              className="mb-4 flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Exit Quiz</span>
            </Button>
            
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-3xl font-bold text-foreground">{quiz.title}</h1>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2 text-foreground">
                  <Clock className="w-5 h-5" />
                  <span className="font-mono text-lg">{formatTime(timeLeft)}</span>
                </div>
                {timeLeft < 120 && (
                  <Badge variant="destructive" className="flex items-center space-x-1">
                    <AlertTriangle className="w-3 h-3" />
                    <span>Time Warning</span>
                  </Badge>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>Question {currentQuestion + 1} of {questions.length}</span>
                <span>{Math.round(progress)}% Complete</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          </div>

          {/* Question */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="text-xl">
                Question {currentQuestion + 1}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-lg mb-6">{currentQ.question}</p>
              
              <div className="space-y-3">
                {currentQ.options.map((option, index) => (
                  <button
                    key={index}
                    onClick={() => handleAnswerSelect(index)}
                    className={`w-full p-4 text-left rounded-lg border transition-all ${
                      selectedAnswers[currentQuestion] === index
                        ? "border-primary bg-primary/10"
                        : "border-border hover:border-primary/50 hover:bg-primary/5"
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-4 h-4 rounded-full border-2 ${
                        selectedAnswers[currentQuestion] === index
                          ? "border-primary bg-primary"
                          : "border-border"
                      }`} />
                      <span>{option}</span>
                    </div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Navigation */}
          <div className="flex justify-between">
            <Button 
              variant="outline" 
              onClick={handlePrevious}
              disabled={currentQuestion === 0}
            >
              Previous
            </Button>
            
            <div className="space-x-3">
              {currentQuestion < questions.length - 1 ? (
                <Button 
                  onClick={handleNext}
                  disabled={selectedAnswers[currentQuestion] === undefined}
                >
                  Next Question
                </Button>
              ) : (
                <Button 
                  onClick={handleSubmit}
                  disabled={Object.keys(selectedAnswers).length < questions.length}
                  className="bg-learning-success hover:bg-learning-success/90"
                >
                  Submit Quiz
                </Button>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default QuizInterface;