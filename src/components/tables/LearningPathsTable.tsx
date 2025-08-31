import React from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Eye, Edit } from "lucide-react";
import DeleteLearningPathDialog from "@/components/dialogs/DeleteLearningPathDialog";
import EditLearningPathDialog from "@/components/dialogs/EditLearningPathDialog";
import ViewLearningPathDialog from "@/components/dialogs/ViewLearningPathDialog";
import { LearningPath } from "@/types";

interface LearningPathsTableProps {
  learningPaths: LearningPath[];
  getDifficultyColor: (difficulty: string) => string;
  getStatusColor: (status: string) => string;
  viewPath: LearningPath | null;
  setViewPath: (lp: LearningPath | null) => void;
  editPath: LearningPath | null;
  setEditPath: (lp: LearningPath | null) => void;
  deleteId: string | null;
  setDeleteId: (id: string | null) => void;
  availableModules: any[];
  modulesLoading: boolean;
  modulesError: string | null;
  openModulesDropdownFor: string | null;
  setOpenModulesDropdownFor: (id: string | null) => void;
  editMutation: any;
  deleteMutation: any;
}

const LearningPathsTable: React.FC<LearningPathsTableProps> = ({
  learningPaths,
  getDifficultyColor,
  getStatusColor,
  viewPath,
  setViewPath,
  editPath,
  setEditPath,
  deleteId,
  setDeleteId,
  availableModules,
  modulesLoading,
  modulesError,
  openModulesDropdownFor,
  setOpenModulesDropdownFor,
  editMutation,
  deleteMutation,
}) => (
  <Table>
    <TableHeader>
      <TableRow>
  <TableHead>Learning Path</TableHead>
  <TableHead>Duration</TableHead>
        <TableHead>Difficulty</TableHead>
        <TableHead>Enrolled</TableHead>
        
        <TableHead>Actions</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      {learningPaths.map((path) => (
        <TableRow key={path.id}>
          <TableCell>
            <div>
              <p className="font-medium">{path.title}</p>
              <p className="text-sm text-muted-foreground">{path.description}</p>
            </div>
          </TableCell>
          <TableCell>{path.duration}</TableCell>
          <TableCell>
            <Badge className={`${getDifficultyColor(path.difficulty)} text-white`}>
              {path.difficulty}
            </Badge>
          </TableCell>
          <TableCell>
            <span className="font-semibold">{path.enrolledUsers || 0}</span> users
          </TableCell>
          
          <TableCell>
            <div className="flex space-x-2">
              <Button variant="ghost" size="sm" onClick={() => setViewPath(path)}>
                <Eye className="w-4 h-4" />
              </Button>
              <ViewLearningPathDialog open={!!viewPath && viewPath.id === path.id} onOpenChange={open => setViewPath(open ? path : null)} viewPath={viewPath} />
              <Button variant="ghost" size="sm" onClick={() => setEditPath(path)}>
                <Edit className="w-4 h-4" />
              </Button>
              <EditLearningPathDialog
                open={!!editPath && editPath.id === path.id}
                onOpenChange={open => setEditPath(open ? path : null)}
                editPath={editPath}
                setEditPath={setEditPath}
                availableModules={availableModules}
                modulesLoading={modulesLoading}
                modulesError={modulesError}
                openModulesDropdownFor={openModulesDropdownFor}
                setOpenModulesDropdownFor={setOpenModulesDropdownFor}
                editMutation={editMutation}
              />
              <DeleteLearningPathDialog
                open={deleteId === path.id}
                onOpenChange={open => setDeleteId(open ? path.id : null)}
                pathTitle={path.title}
                onDelete={() => deleteMutation.mutate(path.id)}
              />
            </div>
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
);

export default LearningPathsTable;
