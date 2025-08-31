import { Progress } from "@/components/ui/progress";
import { CheckCircle2, Circle } from "lucide-react";

interface Step {
  id: number;
  title: string;
  description: string;
  fields: string[];
}

interface ProgressIndicatorProps {
  currentStep: number;
  totalSteps: number;
  steps: Step[];
}

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({ 
  currentStep, 
  totalSteps, 
  steps 
}) => {
  const progressValue = ((currentStep) / totalSteps) * 100;

  return (
    <div className="mb-8">
      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-muted-foreground">
            Step {currentStep} of {totalSteps}
          </span>
          <span className="text-sm text-muted-foreground">
            {Math.round(progressValue)}% Complete
          </span>
        </div>
        <Progress value={progressValue} className="h-2" />
      </div>

      {/* Step Indicators */}
      <div className="flex justify-between">
        {steps.map((step, index) => (
          <div key={step.id} className="flex flex-col items-center flex-1">
            <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
              index + 1 < currentStep 
                ? 'bg-primary border-primary text-white' 
                : index + 1 === currentStep 
                ? 'border-primary text-primary bg-primary/10'
                : 'border-muted-foreground/30 text-muted-foreground'
            }`}>
              {index + 1 < currentStep ? (
                <CheckCircle2 className="w-4 h-4" />
              ) : (
                <span className="text-sm font-semibold">{step.id}</span>
              )}
            </div>
            <div className="text-center mt-2">
              <div className={`text-xs font-medium ${
                index + 1 <= currentStep ? 'text-primary' : 'text-muted-foreground'
              }`}>
                {step.title}
              </div>
              <div className="text-xs text-muted-foreground mt-1 max-w-20">
                {step.description}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProgressIndicator;
