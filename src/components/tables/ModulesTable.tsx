
import React from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Edit, Trash2, FileText } from "lucide-react";

import { type Module } from "@/types/module";

interface ModulesTableProps {
  modules: Module[];
  onEdit: (mod: Module) => void;
  onDelete: (mod: Module) => void;
  onManageMaterials: (mod: Module) => void;
}

const ModulesTable: React.FC<ModulesTableProps> = ({ modules, onEdit, onDelete, onManageMaterials }) => (
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead>Module ID</TableHead>
        <TableHead>Name</TableHead>
        <TableHead>Description</TableHead>
        <TableHead>Chapters</TableHead>
        <TableHead>Actions</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      {modules.map(mod => (
        <TableRow key={mod.id}>
          <TableCell>{mod.id}</TableCell>
          <TableCell>{mod.title || mod.name}</TableCell>
          <TableCell>{mod.description}</TableCell>
          <TableCell>{mod.chapter_count || mod.chapters?.length || 0}</TableCell>
          <TableCell>
            <div className="flex space-x-2">
              <Button variant="ghost" size="sm" onClick={() => onEdit(mod)}>
                <Edit className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => onManageMaterials(mod)}>
                <FileText className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => onDelete(mod)}>
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
);

export default ModulesTable;
