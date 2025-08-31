import { validatePassword, PasswordValidation } from "@/utils/validation";
import { Progress } from "@/components/ui/progress";
import { CheckCircle2, XCircle } from "lucide-react";

interface PasswordStrengthProps {
  password: string;
  showValidation?: boolean;
}

const PasswordStrength: React.FC<PasswordStrengthProps> = ({ 
  password, 
  showValidation = true 
}) => {
  const validation = validatePassword(password);
  
  if (!password) return null;

  const getStrengthColor = (strength: PasswordValidation['strength']) => {
    switch (strength) {
      case 'weak': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'strong': return 'bg-green-500';
      default: return 'bg-gray-300';
    }
  };

  const getStrengthValue = (strength: PasswordValidation['strength']) => {
    switch (strength) {
      case 'weak': return 25;
      case 'medium': return 60;
      case 'strong': return 100;
      default: return 0;
    }
  };

  return (
    <div className="mt-2">
      {/* Strength Bar */}
      <div className="mb-2">
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs text-muted-foreground">Password Strength</span>
          <span className={`text-xs font-medium ${
            validation.strength === 'strong' ? 'text-green-600' :
            validation.strength === 'medium' ? 'text-yellow-600' : 'text-red-600'
          }`}>
            {validation.strength.charAt(0).toUpperCase() + validation.strength.slice(1)}
          </span>
        </div>
        <Progress 
          value={getStrengthValue(validation.strength)}
          className="h-2"
        />
      </div>

      {/* Validation Messages */}
      {showValidation && (
        <div className="space-y-1">
          {validation.errors.map((error, index) => (
            <div key={index} className="flex items-center gap-2 text-xs text-red-600">
              <XCircle className="w-3 h-3" />
              {error}
            </div>
          ))}
          {validation.isValid && (
            <div className="flex items-center gap-2 text-xs text-green-600">
              <CheckCircle2 className="w-3 h-3" />
              Password meets all requirements
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PasswordStrength;
