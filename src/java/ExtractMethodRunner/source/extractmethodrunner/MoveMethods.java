package extractmethodrunner;

import java.io.ByteArrayInputStream;
import java.io.IOException;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.jdt.core.ICompilationUnit;
import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.PackageDeclaration;

public class MoveMethods {

	public static ICompilationUnit ensureTargetClass(CompilationUnit ast, IProgressMonitor pm, String targetClassName) throws IOException, CoreException {
		IResource javaFile = ast.getJavaElement().getResource();
		IPath otherFilePath = javaFile.getLocation().removeLastSegments(1).append(targetClassName + ".java");
		IFile otherFile = javaFile.getProject().getFile(otherFilePath);
	
		if (! otherFile.exists()) {
			class GetPackage extends ASTVisitor {
				private String pkg;
				
				@Override
				public boolean visit(PackageDeclaration node) {
					pkg = node.getName().getFullyQualifiedName();
					return false;
				}
			}

			GetPackage x = new GetPackage();
			ast.accept(x);
			
			String text = "package " + x.pkg + ";\n\n" +
					"class Other {\n" +
					"}\n";
			
			otherFile.create(new ByteArrayInputStream(text.getBytes()), false, pm);
		}
		
		return JavaCore.createCompilationUnitFrom(otherFile);
	}
	
}
