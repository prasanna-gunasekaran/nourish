export type ConfidenceLevel = 'HIGH' | 'MEDIUM' | 'LOW';

export type MealType = 'Breakfast' | 'Lunch' | 'Snack' | 'Dinner' | 'Other';

export interface FoodItemParsed {
  food_name: string;
  quantity: number;
  unit: string;
  preparation?: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
  confidence: ConfidenceLevel;
  db_item_id?: string;
}

export interface LoggedMeal {
  meal_id: string;
  user_id: string;
  timestamp: string;
  meal_type: MealType;
  food_items: FoodItemParsed[];
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  total_fiber: number;
  confidence: ConfidenceLevel;
  confirmed: boolean;
  metadata?: Record<string, any>;
}

export interface UserProfile {
  user_id: string;
  disliked_foods: string[];
  food_preferences: string[];
  dietary_preferences: string[];
  confirmed_portions: Record<string, string>;
  calorie_goal: number;
  protein_goal: number;
  carbs_goal: number;
  fat_goal: number;
}

export interface Reminder {
  reminder_id: string;
  user_id: string;
  title: string;
  frequency: string;
  active: boolean;
  created_at: string;
}

export interface AgentActionTrace {
  tool_name: string;
  description: string;
  input_data?: Record<string, any>;
  output_summary: string;
  timestamp: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'nourish' | 'system';
  text: string;
  timestamp: string;
  meal_data?: LoggedMeal;
  confirmation_required?: boolean;
  action_traces?: AgentActionTrace[];
}

export interface DashboardData {
  user_id: string;
  today_summary: {
    date: string;
    meal_count: number;
    total_calories: number;
    total_protein: number;
    total_carbs: number;
    total_fat: number;
    total_fiber: number;
    meals: LoggedMeal[];
  };
  user_profile: UserProfile;
  insights: string[];
  reminders: Reminder[];
}
