import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, ArrowRight, ArrowLeft, BookOpen, Eye, Ear, PenTool, Hand, Brain } from "lucide-react";

const varkQuestions = [
  {
    id: 1,
    question: "When you are learning something new, you prefer to:",
    options: [
      { label: "See diagrams, charts, or pictures", value: "Visual", icon: Eye },
      { label: "Listen to explanations or discussions", value: "Aural", icon: Ear },
      { label: "Read instructions or information", value: "Read/Write", icon: PenTool },
      { label: "Try it out and do something physical", value: "Kinesthetic", icon: Hand },
    ],
  },
  {
    id: 2,
    question: "When you give directions, you:",
    options: [
      { label: "Draw a map or show a diagram", value: "Visual", icon: Eye },
      { label: "Tell them how to get there", value: "Aural", icon: Ear },
      { label: "Write down the directions", value: "Read/Write", icon: PenTool },
      { label: "Go with them or point as you go", value: "Kinesthetic", icon: Hand },
    ],
  },
  {
    id: 3,
    question: "When you cook a new dish, you prefer to:",
    options: [
      { label: "Follow a recipe with pictures", value: "Visual", icon: Eye },
      { label: "Have someone explain the steps", value: "Aural", icon: Ear },
      { label: "Follow a written recipe step-by-step", value: "Read/Write", icon: PenTool },
      { label: "Watch someone cook it first", value: "Kinesthetic", icon: Hand },
    ],
  },
  {
    id: 4,
    question: "When you're trying to concentrate, you:",
    options: [
      { label: "Focus on visual elements and avoid clutter", value: "Visual", icon: Eye },
      { label: "Need quiet or prefer background music", value: "Aural", icon: Ear },
      { label: "Make written notes and lists", value: "Read/Write", icon: PenTool },
      { label: "Need to move around or use fidget tools", value: "Kinesthetic", icon: Hand },
    ],
  },
  {
    id: 5,
    question: "When you want to remember a phone number, you:",
    options: [
      { label: "Visualize the keypad and number layout", value: "Visual", icon: Eye },
      { label: "Say it out loud several times", value: "Aural", icon: Ear },
      { label: "Write it down immediately", value: "Read/Write", icon: PenTool },
      { label: "Use finger movements to 'dial' it", value: "Kinesthetic", icon: Hand },
    ],
  },
  {
    id: 6,
    question: "When you're at a conference or meeting, you:",
    options: [
      { label: "Focus on slides, diagrams, and visual presentations", value: "Visual", icon: Eye },
      { label: "Listen carefully to what speakers are saying", value: "Aural", icon: Ear },
      { label: "Take detailed written notes", value: "Read/Write", icon: PenTool },
      { label: "Prefer interactive sessions and hands-on activities", value: "Kinesthetic", icon: Hand },
    ],
  },
  {
    id: 7,
    question: "When you're shopping for clothes, you:",
    options: [
      { label: "Look at how items appear and fit visually", value: "Visual", icon: Eye },
      { label: "Ask for opinions and recommendations", value: "Aural", icon: Ear },
      { label: "Read labels, reviews, and size charts", value: "Read/Write", icon: PenTool },
      { label: "Touch fabrics and try everything on", value: "Kinesthetic", icon: Hand },
    ],
  },
  {
    id: 8,
    question: "When you're learning a new software, you:",
    options: [
      { label: "Watch tutorial videos and screenshots", value: "Visual", icon: Eye },
      { label: "Listen to explanations or use voice tutorials", value: "Aural", icon: Ear },
      { label: "Read the manual or step-by-step guides", value: "Read/Write", icon: PenTool },
      { label: "Jump in and learn by doing and experimenting", value: "Kinesthetic", icon: Hand },
    ],
  },
  {
    id: 9,
    question: "When you need to solve a complex problem, you:",
    options: [
      { label: "Draw flowcharts or mind maps", value: "Visual", icon: Eye },
      { label: "Talk it through with someone", value: "Aural", icon: Ear },
      { label: "Make lists and write down the steps", value: "Read/Write", icon: PenTool },
      { label: "Work through examples and practice", value: "Kinesthetic", icon: Hand },
    ],
  },
  {
    id: 10,
    question: "When you're relaxing, you prefer to:",
    options: [
      { label: "Watch movies, look at art, or browse visually", value: "Visual", icon: Eye },
      { label: "Listen to music, podcasts, or conversations", value: "Aural", icon: Ear },
      { label: "Read books, articles, or write", value: "Read/Write", icon: PenTool },
      { label: "Do physical activities or hands-on hobbies", value: "Kinesthetic", icon: Hand },
    ],
  },
  {
    id: 11,
    question: "When you're explaining something to others, you:",
    options: [
      { label: "Use gestures, drawings, or visual aids", value: "Visual", icon: Eye },
      { label: "Explain verbally with examples", value: "Aural", icon: Ear },
      { label: "Provide written instructions or references", value: "Read/Write", icon: PenTool },
      { label: "Demonstrate by doing it yourself", value: "Kinesthetic", icon: Hand },
    ],
  },
  {
    id: 12,
    question: "When you're stressed or overwhelmed, you:",
    options: [
      { label: "Need a clean, organized visual environment", value: "Visual", icon: Eye },
      { label: "Talk to someone or listen to calming sounds", value: "Aural", icon: Ear },
      { label: "Write in a journal or make to-do lists", value: "Read/Write", icon: PenTool },
      { label: "Need to move, exercise, or do something physical", value: "Kinesthetic", icon: Hand },
    ],
  },
];

const learningStyleDescriptions = {
  Visual: {
    title: "Visual Learner",
    description: "You learn best through seeing and visualizing information",
    characteristics: ["Prefer charts, diagrams, and visual aids", "Remember faces better than names", "Like organized, clean environments", "Think in pictures and spatial relationships"],
    tips: ["Use mind maps and flowcharts", "Color-code your notes", "Watch educational videos", "Use visual mnemonics"],
    icon: Eye,
    color: "bg-blue-500"
  },
  Aural: {
    title: "Auditory Learner", 
    description: "You learn best through listening and verbal communication",
    characteristics: ["Enjoy discussions and verbal explanations", "Remember names better than faces", "Like background music", "Think out loud"],
    tips: ["Record and replay lectures", "Join study groups for discussion", "Use acronyms and rhymes", "Read aloud to yourself"],
    icon: Ear,
    color: "bg-green-500"
  },
  "Read/Write": {
    title: "Reading/Writing Learner",
    description: "You learn best through reading and writing activities", 
    characteristics: ["Prefer written instructions", "Love taking notes", "Enjoy reading extensively", "Express thoughts well in writing"],
    tips: ["Take detailed notes", "Create summaries and outlines", "Use lists and bullet points", "Write practice essays"],
    icon: PenTool,
    color: "bg-purple-500"
  },
  Kinesthetic: {
    title: "Kinesthetic Learner",
    description: "You learn best through hands-on experience and physical activity",
    characteristics: ["Need to touch and manipulate objects", "Learn by doing and practicing", "Good at sports and physical activities", "Use gestures when talking"],
    tips: ["Use hands-on activities", "Take breaks to move around", "Use real-world examples", "Build models and prototypes"],
    icon: Hand,
    color: "bg-orange-500"
  }
};

const VARKQuiz: React.FC = () => {
  const [answers, setAnswers] = useState<string[]>(Array(varkQuestions.length).fill(""));
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [submitted, setSubmitted] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const navigate = useNavigate();

  const handleAnswer = (value: string) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = value;
    setAnswers(newAnswers);
  };

  const nextQuestion = () => {
    if (currentQuestion < varkQuestions.length - 1) {
      setIsTransitioning(true);
      setTimeout(() => {
        setCurrentQuestion(prev => prev + 1);
        setIsTransitioning(false);
      }, 150);
    }
  };

  const prevQuestion = () => {
    if (currentQuestion > 0) {
      setIsTransitioning(true);
      setTimeout(() => {
        setCurrentQuestion(prev => prev - 1);
        setIsTransitioning(false);
      }, 150);
    }
  };

  const calculateResults = () => {
    const counts: Record<string, number> = {
      Visual: 0,
      Aural: 0,
      "Read/Write": 0,
      Kinesthetic: 0
    };
    
    answers.forEach((answer) => {
      if (answer && counts.hasOwnProperty(answer)) {
        counts[answer]++;
      }
    });
    
    const total = answers.length;
    const percentages = Object.entries(counts).map(([style, count]) => ({
      style,
      count,
      percentage: Math.round((count / total) * 100)
    })).sort((a, b) => b.count - a.count);
    
    const primaryStyle = percentages[0].style;
    
    return {
      primaryStyle,
      percentages,
      counts
    };
  };

  const handleSubmit = async () => {
    const results = calculateResults();
    setResults(results);
    setSubmitted(true);
    
    // Save results to backend and localStorage
    try {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      const userId = user.id || user.user_id;
      
      // Save to backend
      await fetch('/api/learning-style', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          learning_style: results.primaryStyle,
          vark_scores: results.counts,
          quiz_date: new Date().toISOString()
        }),
      });
      
      // Save to localStorage
      localStorage.setItem("learningStyle", results.primaryStyle);
      localStorage.setItem("varkResults", JSON.stringify(results));
      
    } catch (error) {
      console.error('Failed to save learning style:', error);
    }
  };

  const completedQuestions = answers.filter(a => a !== "").length;
  const progress = (completedQuestions / varkQuestions.length) * 100;

  if (submitted && results) {
    const primaryStyleInfo = learningStyleDescriptions[results.primaryStyle as keyof typeof learningStyleDescriptions];
    const PrimaryIcon = primaryStyleInfo.icon;
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-background to-muted/30 p-4">
        <div className="max-w-4xl mx-auto">
          <Card className="mb-6">
            <CardHeader className="text-center">
              <div className="flex items-center justify-center mb-4">
                <div className={`p-4 rounded-full ${primaryStyleInfo.color} text-white`}>
                  <PrimaryIcon className="w-8 h-8" />
                </div>
              </div>
              <CardTitle className="text-3xl font-bold">Quiz Complete!</CardTitle>
              <CardDescription className="text-lg">
                Your primary learning style is <Badge variant="secondary" className="mx-1">{primaryStyleInfo.title}</Badge>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-xl font-semibold mb-3">Your Learning Profile</h3>
                  <p className="text-muted-foreground mb-4">{primaryStyleInfo.description}</p>
                  
                  <div className="space-y-3">
                    {results.percentages.map(({ style, percentage, count }: any) => {
                      const styleInfo = learningStyleDescriptions[style as keyof typeof learningStyleDescriptions];
                      const StyleIcon = styleInfo.icon;
                      return (
                        <div key={style} className="flex items-center gap-3">
                          <div className={`p-2 rounded ${styleInfo.color} text-white`}>
                            <StyleIcon className="w-4 h-4" />
                          </div>
                          <div className="flex-1">
                            <div className="flex justify-between text-sm">
                              <span>{style}</span>
                              <span>{percentage}% ({count}/{varkQuestions.length})</span>
                            </div>
                            <Progress value={percentage} className="h-2 mt-1" />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
                
                <div>
                  <h3 className="text-xl font-semibold mb-3">Key Characteristics</h3>
                  <ul className="space-y-2 mb-4">
                    {primaryStyleInfo.characteristics.map((char: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-1 flex-shrink-0" />
                        <span className="text-sm">{char}</span>
                      </li>
                    ))}
                  </ul>
                  
                  <h3 className="text-xl font-semibold mb-3">Learning Tips</h3>
                  <ul className="space-y-2">
                    {primaryStyleInfo.tips.map((tip: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2">
                        <Brain className="w-4 h-4 text-blue-500 mt-1 flex-shrink-0" />
                        <span className="text-sm">{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              
              <div className="mt-6 pt-6 border-t text-center">
                <p className="text-muted-foreground mb-4">
                  Your learning style will help us customize your onboarding experience and recommend the most effective learning materials for you.
                </p>
                <Button 
                  onClick={() => {
                    // Start the onboarding workflow
                    setTimeout(() => navigate("/dashboard"), 1000);
                  }}
                  size="lg"
                  className="w-full md:w-auto"
                >
                  Continue to Dashboard
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const currentQ = varkQuestions[currentQuestion];
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/30 p-4">
      <div className="max-w-2xl mx-auto">
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between mb-2">
              <Badge variant="outline" className="flex items-center gap-1">
                <BookOpen className="w-4 h-4" />
                VARK Learning Style Assessment
              </Badge>
              <span className="text-sm text-muted-foreground">
                Question {currentQuestion + 1} of {varkQuestions.length}
              </span>
            </div>
            <div className="mb-4">
              <Progress value={(currentQuestion + 1) / varkQuestions.length * 100} className="h-2" />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>Progress</span>
                <span>{Math.round((currentQuestion + 1) / varkQuestions.length * 100)}% Complete</span>
              </div>
            </div>
            <CardTitle className="text-xl">{currentQ.question}</CardTitle>
            <CardDescription>
              Select the option that best describes your preference
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className={`space-y-3 transition-opacity duration-150 ${isTransitioning ? 'opacity-50' : 'opacity-100'}`}>
              {currentQ.options.map((option, idx) => {
                const OptionIcon = option.icon;
                const isSelected = answers[currentQuestion] === option.value;
                return (
                  <button
                    key={option.value}
                    onClick={() => handleAnswer(option.value)}
                    className={`w-full p-4 text-left border rounded-lg transition-all hover:border-primary/50 hover:bg-muted/50 ${
                      isSelected 
                        ? 'border-primary bg-primary/10 shadow-sm' 
                        : 'border-border'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded ${isSelected ? 'bg-primary text-white' : 'bg-muted'}`}>
                        <OptionIcon className="w-4 h-4" />
                      </div>
                      <span className="flex-1">{option.label}</span>
                      {isSelected && (
                        <CheckCircle className="w-5 h-5 text-primary" />
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
            
            <div className="flex justify-between items-center mt-6">
              <Button
                variant="outline"
                onClick={prevQuestion}
                disabled={currentQuestion === 0}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                Previous
              </Button>
              
              <div className="text-sm text-muted-foreground">
                {completedQuestions} of {varkQuestions.length} answered
              </div>
              
              {currentQuestion === varkQuestions.length - 1 ? (
                <Button
                  onClick={handleSubmit}
                  disabled={!answers[currentQuestion]}
                  className="flex items-center gap-2"
                >
                  Complete Quiz
                  <CheckCircle className="w-4 h-4" />
                </Button>
              ) : (
                <Button
                  onClick={nextQuestion}
                  disabled={!answers[currentQuestion]}
                  className="flex items-center gap-2"
                >
                  Next
                  <ArrowRight className="w-4 h-4" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
        
        {/* Progress Overview */}
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <h3 className="font-semibold mb-2">Overall Progress</h3>
              <Progress value={progress} className="mb-2" />
              <p className="text-sm text-muted-foreground">
                {completedQuestions} questions completed ({Math.round(progress)}%)
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default VARKQuiz;
